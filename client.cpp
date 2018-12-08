#include <pybind11/pybind11.h>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/regex.hpp>
#include <iostream>
#include <string>

namespace py = pybind11;

class Client {
   private:
    boost::asio::io_context& io_context;
    boost::asio::ip::tcp::socket socket;

   public:
    std::string head;
    std::string tail;

   public:
    Client(boost::asio::io_context& io_context_) : io_context(io_context_), socket(io_context_) {}

    void connect(const boost::asio::ip::tcp::endpoint& endpoint) {
        boost::system::error_code error_code;
        socket.connect(endpoint, error_code);

        if (error_code) {
            std::cout << "connect failed: " << error_code.message() << std::endl;
        } else {
            std::cout << "connect succeeded: " << socket.remote_endpoint() << std::endl;
        }
    }

    void send(const std::string& string) {
        boost::asio::async_write(socket, boost::asio::buffer("<s>" + string + "</s>"), [this, string](auto error_code, auto size) {
            if (error_code) {
                std::cout << "send failed: " << error_code.message() << std::endl;
            } else {
                std::cout << "send succeeded: " << string << std::endl;

                receive();
            }
        });
    }

    void receive() {
        boost::asio::async_read_until(socket, boost::asio::dynamic_buffer(tail), boost::regex("<s>.*</s>"), [this](auto error_code, auto size) {
            if (error_code) {
                std::cout << "receive failed: " << error_code.message() << std::endl;

                socket.close();

            } else {
                std::string start_token = "<s>";
                std::string end_token = "</s>";

                head = std::string(std::search(tail.begin(), tail.end(), start_token.begin(), start_token.end()) + start_token.size(),
                                   std::search(tail.begin(), tail.end(), end_token.begin(), end_token.end()));
                std::cout << "receive succeeded: " << head << std::endl;

                tail.erase(0, size);
            }
        });
    }
};

PYBIND11_MODULE(client, module) {
    module.def("request", [](const std::string& ip_address, const std::string& port_number, const std::string& string) {
        boost::asio::io_context io_context;
        Client client(io_context);

        boost::asio::ip::tcp::endpoint endpoint(boost::asio::ip::address::from_string(ip_address), std::stoi(port_number));
        client.connect(endpoint);
        client.send(string);

        io_context.run();

        return client.head;
    });
}

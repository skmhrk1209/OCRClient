#include <pybind11/pybind11.h>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/regex.hpp>
#include <iostream>
#include <string>
#include <tuple>

namespace py = pybind11;
namespace asio = boost::asio;

class Client {
    struct Socket {
        template <typename... Args>
        Socket(Args&&... args) : socket(std::forward<Args>(args)...) {}
        asio::ip::tcp::socket socket;
        std::string send_buffer;
        std::string receive_buffer;
    };

   private:
    asio::io_context& io_context;
    Socket socket;

    const std::string sos = "<s>";
    const std::string eos = "</s>";

   public:
    Client(asio::io_context& context) : io_context(context), socket(context) {}

    bool connect(const asio::ip::tcp::endpoint& endpoint) {
        boost::system::error_code error_code;
        socket.socket.connect(endpoint, error_code);

        if (error_code) {
            std::cout << "connect failed: " << error_code.message() << std::endl;

            return false;
        } else {
            std::cout << "connect succeeded: " << socket.socket.remote_endpoint() << std::endl;

            return true;
        }
    }

    void send(const std::string& string) {
        socket.send_buffer = sos + string + eos;

        asio::async_write(socket.socket, asio::buffer(socket.send_buffer), [this](auto error_code, ...) {
            if (error_code) {
                std::cout << "send failed: " << error_code.message() << std::endl;

                socket.socket.close();
            } else {
                std::cout << "send succeeded" << std::endl;

                receive();
            }
        });
    }

    void receive() {
        asio::async_read_until(socket.socket, asio::dynamic_buffer(socket.receive_buffer), boost::regex(sos + ".*" + eos), [this](auto error_code, ...) {
            if (error_code) {
                std::cout << "receive failed: " << error_code.message() << std::endl;

                socket.socket.close();
            } else {
                std::cout << "receive succeeded" << std::endl;

                socket.receive_buffer.erase(socket.receive_buffer.begin(), socket.receive_buffer.begin() + sos.size());
                socket.receive_buffer.erase(socket.receive_buffer.end() - eos.size(), socket.receive_buffer.end());
            }
        });
    }

    std::string received() const { return socket.receive_buffer; }
};

PYBIND11_MODULE(client, module) {
    module.def("request", [](const std::string& ip_address, const std::string& port_number, const std::string& string) -> std::string {
        asio::io_context io_context;
        Client client(io_context);

        asio::ip::tcp::endpoint endpoint(asio::ip::address::from_string(ip_address), std::stoi(port_number));

        if (client.connect(endpoint)) {
            client.send(string);

            io_context.run();

            return client.received();
        }
    });
}

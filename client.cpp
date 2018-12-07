#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/regex.hpp>
#include <iostream>
#include <string>
#include <unordered_map>

class Client {
   private:
    boost::asio::io_context& io_context;
    boost::asio::ip::tcp::socket socket;
    std::string buffer;

   public:
    Client(boost::asio::io_context& io_context_) : io_context(io_context_), socket(io_context_) {}

    void connect(const boost::asio::ip::tcp::endpoint& endpoint) {
        socket.async_connect(endpoint, [this](auto error_code) {
            if (error_code) {
                std::cout << "connect failed: " << error_code.message() << std::endl;
            } else {
                std::cout << "connect succeeded: " << socket.remote_endpoint() << std::endl;
            }
        });
    }

    void send(const std::string& string) {
        boost::asio::async_write(socket, boost::asio::buffer(string), [this, string](auto error_code, auto size) {
            if (error_code) {
                std::cout << "send failed: " << error_code.message() << std::endl;
            } else {
                std::cout << "send succeeded: " << string << std::endl;
            }
        });
    }

    void receive() {
        boost::asio::async_read_until(socket, boost::asio::dynamic_buffer(buffer), boost::regex("<s>.*</s>"), [this](auto error_code, auto size) {
            if (error_code) {
                std::cout << "receive failed: " << error_code.message() << std::endl;

                socket.close();

            } else {
                std::string string = buffer.substr(3, size - 7);
                std::cout << "receive succeeded: " << string << std::endl;
            }
        });
    }
};

int main(int argc, char* argv[]) {
    boost::asio::io_context io_context;

    Client client(io_context);

    boost::asio::ip::tcp::endpoint endpoint(boost::asio::ip::address::from_string(argv[1]), std::atoi(argv[2]));
    client.connect(endpoint);
    io_context.run();

    std::string string;
    while (std::getline(std::cin, string)) {
        io_context.restart();
        client.send("<s>" + string + "</s>");
        client.receive();
        io_context.run();
    }
}
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <iostream>
#include <string>

class Client {
    boost::asio::io_context& io_context;
    boost::asio::ip::tcp::socket socket;

   public:
    Client(boost::asio::io_context& io_context_) : io_context(io_context_), socket(io_context_) {}

    void connect(const boost::asio::ip::tcp::endpoint& endpoint) {
        socket.async_connect(endpoint, [this](const boost::system::error_code& error_code) {
            if (error_code) {
                std::cout << "connect failed: " << error_code.message() << std::endl;
            } else {
                std::cout << "connect succeeded: " << socket.remote_endpoint() << std::endl;
            }
        });
    }

    void send(const std::string& data) {
        boost::asio::async_write(socket, boost::asio::buffer(data), [&](const boost::system::error_code& error_code, size_t bytes_transferred) {
            if (error_code) {
                std::cout << "send failed: " << error_code.message() << std::endl;
            } else {
                std::cout << "send succeeded: " << data << std::endl;
            }
        });
    }
};

int main(int argc, char* argv[]) {
    boost::asio::io_context io_context;

    Client client(io_context);

    boost::asio::ip::tcp::endpoint endpoint(boost::asio::ip::address::from_string(argv[1]), std::atoi(argv[2]));
    client.connect(endpoint);

    client.send("fuck\n");

    io_context.run();
}
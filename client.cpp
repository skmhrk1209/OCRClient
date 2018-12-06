#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <iostream>
#include <string>

namespace asio = boost::asio;
using asio::ip::tcp;

class Client {
    boost::asio::io_service& io_service;
    tcp::socket socket;

   public:
    Client(boost::asio::io_service& io_service_) : io_service(io_service_), socket(io_service_) {}

    void connect(const std::string& ip, unsigned short port) {
        socket.async_connect(tcp::endpoint(boost::asio::ip::address::from_string(ip), port),
                             boost::bind(&Client::on_connect, this, boost::asio::placeholders::error));
    }

    void send(const std::string& data) {
        boost::asio::async_write(socket, boost::asio::buffer(data),
                                 boost::bind(&Client::on_send, this, boost::asio::placeholders::error, asio::placeholders::bytes_transferred));
    }

   private:
    void on_connect(const boost::system::error_code& error_code) {
        if (error_code) {
            std::cout << "connect failed: " << error_code.message() << std::endl;
            return;
        }

        send("fuck");
    }

    void on_send(const boost::system::error_code& error_code, size_t bytes_transferred) {
        if (error_code) {
            std::cout << "send failed: " << error_code.message() << std::endl;
            return;
        }
    }
};

int main() {
    asio::io_service io_service;

    Client client(io_service);

    client.connect("192.168.6.116", 31400);

    io_service.run();
}
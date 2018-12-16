#include <pybind11/pybind11.h>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/regex.hpp>
#include <iostream>
#include <memory>
#include <string>

namespace py = pybind11;
namespace asio = boost::asio;

class Client {
   private:
    asio::io_context& io_context;
    asio::ip::tcp::socket socket;

   public:
    Client(asio::io_context& context) : io_context(context), socket(context) {}

    bool connect(const asio::ip::tcp::endpoint& endpoint) {
        boost::system::error_code error_code;
        socket.connect(endpoint, error_code);

        if (error_code) {
            std::cout << "connect failed: " << error_code.message() << std::endl;
            return false;
        } else {
            std::cout << "connect succeeded: " << socket.remote_endpoint() << std::endl;
            return true;
        }
    }

    void write(std::string&& data) {
        std::string write_buffer(std::move(data));
        write_buffer.push_back('\n');
        boost::system::error_code error_code;
        asio::write(socket, asio::buffer(write_buffer), error_code);

        if (error_code) {
            std::cout << "write failed: " << error_code.message() << std::endl;
        } else {
            std::cout << "write succeeded" << std::endl;
        }
    }

    std::string read() {
        std::string read_buffer;
        boost::system::error_code error_code;
        asio::read_until(socket, asio::dynamic_buffer(read_buffer), '\n', error_code);
        read_buffer.pop_back();

        if (error_code) {
            std::cout << "read failed: " << error_code.message() << std::endl;
        } else {
            std::cout << "read succeeded" << std::endl;
        }

        return read_buffer;
    }
};

PYBIND11_MODULE(client, module) {
    module.def("request", [](const std::string& ip_address, const std::string& port_number, std::string&& data) -> std::string {
        asio::io_context io_context;
        asio::ip::tcp::endpoint endpoint(asio::ip::address::from_string(ip_address), std::stoi(port_number));
        Client client(io_context);
        if (client.connect(endpoint)) return client.write(std::move(data)), client.read();
    });
}
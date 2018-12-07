clang++ -std=c++14 -shared -fPIC client.cpp -o client.so \
-I/usr/local/Cellar/python/3.7.1/Frameworks/Python.framework/Versions/3.7/include/python3.7m \
-L/usr/local/Cellar/python/3.7.1/Frameworks/Python.framework/Versions/3.7/lib \
-lboost_system -lboost_regex -lpython3.7m

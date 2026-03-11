cmake_minimum_required(VERSION 3.21)
project(DigitalHumanTwin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets)

add_executable(DigitalHumanTwin
    src/main.cpp
    src/app/MainWindow.cpp
)

target_include_directories(DigitalHumanTwin PRIVATE src)
target_link_libraries(DigitalHumanTwin PRIVATE Qt6::Widgets)

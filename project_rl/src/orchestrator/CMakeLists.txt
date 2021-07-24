cmake_minimum_required(VERSION 2.8.3)
project(orchestrator)

include(CheckCXXCompilerFlag)

CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)

if(COMPILER_SUPPORTS_CXX11)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wl,--no-as-needed")
elseif(COMPILER_SUPPORTS_CXX0X)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
endif()

find_package(catkin REQUIRED COMPONENTS
	roscpp
	rospy
	std_msgs
        message_generation
	)

add_message_files(
        FILES
        float32array.msg
        )

generate_messages(
	DEPENDENCIES 
	std_msgs
	)

catkin_package(
	CATKIN_DEPENDS message_runtime
	CATKIN_DEPENDS std_msgs
	)




# Makefile for trajectory_validator

CXX = g++
CXXFLAGS = -std=c++11 -O2 -Wall -Wextra
TARGET = trajectory_validator
SOURCE = trajectory_validator.cpp

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCE) -lm

clean:
	rm -f $(TARGET)

test: $(TARGET)
	@echo "Testing trajectory validator..."
	@./$(TARGET) 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0
	@echo "Test completed."

.PHONY: all clean test


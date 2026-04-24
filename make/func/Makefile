# thanks Gemini :P
# What you have to do is
# 1. Find all .c files in src/
# 2. Exclude any file ending in '_test.c' or '_experimental.c'
# 3. Place all .o files into a directory called 'build/'

# below is the "bad" way of doing it. It hardcodes a lot and is repetitive
# use some functions like patsubst, filter, etc to make it clean

CC = gcc
CFLAGS = -Wall -Iinclude
TARGET = software_v1

SOURCES = src/main.c src/auth.c src/network.c src/ui.c src/auth_test.c # hardcoded! we don't want that!
OBJECTS = build/main.o build/auth.o build/network.o build/ui.o

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) -o $(TARGET)

# writing the same thing over and over sure isn't fun, especially if there were like 30 files :|

build/main.o: src/main.c
	mkdir -p build
	$(CC) $(CFLAGS) -c src/main.c -o build/main.o

build/auth.o: src/auth.c
	mkdir -p build
	$(CC) $(CFLAGS) -c src/auth.c -o build/auth.o

build/network.o: src/network.c
	mkdir -p build
	$(CC) $(CFLAGS) -c src/network.c -o build/network.o

build/ui.o: src/ui.c
	mkdir -p build
	$(CC) $(CFLAGS) -c src/ui.c -o build/ui.o

clean:
	rm -rf build $(TARGET)
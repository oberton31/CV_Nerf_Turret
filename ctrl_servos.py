import socket
import pigpio
import time

pan_pin = 18
tlt_pin = 17
MIN_PULSEWIDTH = 550
MAX_PULSEWIDTH = 2350

def calc_pulsewidth(angle):
    if angle >= -90:
        return 550 + (((angle + 90) / 180) * (2350 - 550))
    else:
        return 550
def adjust_servos():
    pi.set_mode(pan_pin, pigpio.OUTPUT)
    pi.set_mode(tlt_pin, pigpio.OUTPUT)
    pi.set_servo_pulsewidth(pan_pin, calc_pulsewidth(0))
    pi.set_servo_pulsewidth(tlt_pin, calc_pulsewidth(0))
    
    while True:
        angles = conn.recv(1024).decode("utf-8").split(" ")
        try:
            pan = int(angles[0])
            tlt = int(angles[1])
            pi.set_servo_pulsewidth(pan_pin, calc_pulsewidth(pan))
            pi.set_servo_pulsewidth(tlt_pin, calc_pulsewidth(tlt))
            time.sleep(0.1)
        except ValueError:
            print("Lost Connection")
            pi.set_servo_pulsewidth(pan_pin, calc_pulsewidth(0))
            pi.set_servo_pulsewidth(tlt_pin, calc_pulsewidth(0))

if __name__ == "__main__":
    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    conn, addr = server_socket.accept()
    print("Connected!")
    try:
        pi = pigpio.pi()
        adjust_servos()
    except KeyboardInterrupt:
        pi.set_servo_pulsewidth(pan_pin, 0)
        pi.set_servo_pulsewidth(tlt_pin, 0)
        pi.stop()
        print("Terminated!")



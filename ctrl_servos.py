import socket
import pigpio
import time

pan_pin = 22
tlt_pin_1 = 18
tlt_pin_2 = 17
trig_pin = 23
MIN_PULSEWIDTH = 550
MAX_PULSEWIDTH = 2350

def calc_pulsewidth(angle):
    if angle >= -90:
        return 550 + (((angle + 90) / 180) * (2350 - 550))
    else:
        return 550
    
def move_turret(pan, tlt):
    if pan <= 90 and pan >= -90:
        pi.set_servo_pulsewidth(pan_pin, calc_pulsewidth(pan))
    if tlt <= 45 and tlt >= -45:
        pi.set_servo_pulsewidth(tlt_pin_1, calc_pulsewidth(tlt))
        pi.set_servo_pulsewidth(tlt_pin_2, calc_pulsewidth(-1 * (tlt)))

def pull_trig():
    pi.set_servo_pulsewidth(trig_pin, calc_pulsewidth(-90))
    time.sleep(0.3)
    pi.set_servo_pulsewidth(trig_pin, calc_pulsewidth(0))
    time.sleep(0.3)

def adjust_servos():
    pi.set_mode(pan_pin, pigpio.OUTPUT)
    pi.set_mode(tlt_pin_1, pigpio.OUTPUT)
    pi.set_mode(tlt_pin_2, pigpio.OUTPUT)
    pi.set_mode(trig_pin, pigpio.OUTPUT)
    pi.set_servo_pulsewidth(pan_pin, calc_pulsewidth(0))
    pi.set_servo_pulsewidth(tlt_pin_1, calc_pulsewidth(0))
    pi.set_servo_pulsewidth(tlt_pin_2, calc_pulsewidth(0))
    pi.set_servo_pulsewidth(trig_pin, calc_pulsewidth(0))


    prev_tlt = 0
    prev_pan = 0


    while True:
        info = conn.recv(1024).decode("utf-8").split(" ")
        pan = int(info[0])
        tlt = int(info[1])
        pull_trigger = info[2]
        
        if pull_trigger == '1':
            #move_turret(pan+prev_pan, tlt+prev_tlt)
            pull_trig()
        else:
            move_turret(pan+prev_pan, tlt+prev_tlt)
            


        prev_pan += pan
        prev_tlt += tlt
            
        


if __name__ == "__main__":
    port = 5000
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', port))
        server_socket.listen(1)
        conn, addr = server_socket.accept()
        print("Connected!")
        try:
            pi = pigpio.pi()
            adjust_servos()
        except KeyboardInterrupt:
            pi.set_servo_pulsewidth(pan_pin, 0)
            pi.set_servo_pulsewidth(tlt_pin_1, 0)
            pi.set_servo_pulsewidth(tlt_pin_2, 0)

            pi.stop()
            print("Terminated!")
            break
        except ValueError:
            print("Lost Connection")
            pi.set_servo_pulsewidth(pan_pin, calc_pulsewidth(0))
            pi.set_servo_pulsewidth(tlt_pin_1, calc_pulsewidth(0))
            pi.set_servo_pulsewidth(tlt_pin_2, 0)

            server_socket.shutdown(socket.SHUT_RDWR)
            server_socket.close()




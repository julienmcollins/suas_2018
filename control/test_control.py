import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, dname + '/../util')
sys.path.insert(0, dname + '/flight_control')
import time
import signal
import unittest
from unittest import TestLoader, TestSuite, TextTestRunner

import process_manager
import copter_interface

class TestControl(unittest.TestCase):
    def setUp(self):
        self.test_drone = process_manager.ProcessManager()
        signal.signal(signal.SIGINT, self.test_drone.killall_signalled)

    def tearDown(self):
        self.test_drone.killall()

    def tearDownModule(self):
        self.test_drone.killall()

    def test_init(self):
        drone_address = self.spawn_simulated_drone(0.0, 0.0, 0.0, 0)
        copter = copter_interface.CopterInterface(drone_address)

        time.sleep(12.0)

        sensors = copter.sensor_reader.sensors.get()

        # Make sure we are filling in all our sensor values after initialization
        # of the flight controller.
        self.assertTrue(sensors["state"].get() is not None)
        self.assertTrue(sensors["pixhawk_state"].get() is not None)
        self.assertTrue(sensors["armed"].get() is not None)
        self.assertTrue(sensors["voltage"].get() is not None)
        self.assertTrue(sensors["last_heartbeat"].get() is not None)
        self.assertTrue(sensors["velocity_x"].get() is not None)
        self.assertTrue(sensors["velocity_y"].get() is not None)
        self.assertTrue(sensors["velocity_z"].get() is not None)
        self.assertTrue(sensors["pitch"].get() is not None)
        self.assertTrue(sensors["roll"].get() is not None)
        self.assertTrue(sensors["yaw"].get() is not None)
        self.assertTrue(sensors["heading"].get() is not None)
        self.assertTrue(sensors["ground_speed"].get() is not None)
        self.assertTrue(sensors["air_speed"].get() is not None)

        copter.stop()

    def test_takeoff_and_land(self):
        drone_address = self.spawn_simulated_drone(0.0, 0.0, 0.0, 0)
        copter = copter_interface.CopterInterface(drone_address)

        time.sleep(4.0)

        sensors = copter.sensor_reader.sensors.get()
        print sensors["state"].get()
        self.assertTrue(sensors["state"].get() == "STANDBY")
        self.assertTrue(sensors["armed"].get() == "False")

        copter.controller.set_state("ARM")

        for i in range(0, 18):
            sensors = copter.sensor_reader.sensors.get()
            print "Last heartbeat: " + str(sensors["last_heartbeat"].get()) + \
                  " State: " + copter.controller.get_state()
            time.sleep(1.0)

        # Make sure we get stable values after flight controller initialization.
        sensors = copter.sensor_reader.sensors.get()

        self.assertTrue(sensors["state"].get() == "ARMED")
        self.assertTrue(sensors["armed"].get() == "True")
        self.assertGreater(sensors["voltage"].get(), 12.3)
        self.assertLess(abs(sensors["gps_rel_alt"].get()), 0.1)
        self.assertGreater(sensors["gps_satellites"].get(), 8)

        copter.controller.set_state("TAKEOFF")

        print "Taking off!"

        for i in range(0, 10):
            sensors = copter.sensor_reader.sensors.get()

            print "Lat: " + '%9s' % str(sensors["gps_lat"].get()) + \
                  " Lng: " + '%9s' % str(sensors["gps_lng"].get()) + \
                  " Alt: " + '%9s' % str(sensors["gps_alt"].get()) + \
                  " Ground speed: " + '%9s' % str(sensors["ground_speed"].get())

            time.sleep(1.0)

        self.assertLess(abs(3.0 - abs(sensors["gps_rel_alt"].get())), 0.1)

        copter.controller.set_state("VELOCITY_CONTROL")

        print "Switching to velocity control!"

        for i in range(0, 10):
            sensors = copter.sensor_reader.sensors.get()

            print "Lat: " + '%9s' % str(sensors["gps_lat"].get()) + \
                  " Lng: " + '%9s' % str(sensors["gps_lng"].get()) + \
                  " Alt: " + '%9s' % str(sensors["gps_alt"].get()) + \
                  " Ground speed: " + '%9s' % str(sensors["ground_speed"].get())

            time.sleep(1.0)

        print "Landing!"
        copter.controller.set_state("LAND")

        for i in range(0, 12):
            sensors = copter.sensor_reader.sensors.get()

            print "Lat: " + '%9s' % str(sensors["gps_lat"].get()) + \
                  " Lng: " + '%9s' % str(sensors["gps_lng"].get()) + \
                  " Alt: " + '%9s' % str(sensors["gps_alt"].get()) + \
                  " Ground speed: " + '%9s' % str(sensors["ground_speed"].get())

            time.sleep(1.0)

        self.assertTrue(sensors["state"].get() == "LANDED")
        self.assertLess(abs(sensors["gps_rel_alt"].get()), 0.3)

        copter.stop()

    def spawn_simulated_drone(self, lat, lng, alt, instance):
        self.test_drone.spawn_process("python " + \
                dname + "/flight_control/simulate_copter.py " + \
                "copter " + \
                "--home " + str(lat) + "," \
                          + str(lng) + "," \
                          + str(alt) + ",0 " + \
                "--instance " + str(instance))

        port = 5760 + 10 * instance
        return "tcp:127.0.0.1:" + str(port)

if __name__ == "__main__":
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(TestControl),
    ))

    runner = TextTestRunner(verbosity = 2)

    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)

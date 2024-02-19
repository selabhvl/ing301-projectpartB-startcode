import unittest
from smarthouse.persistence import SmartHouseRepository
from pathlib import Path

class SmartHouseTest(unittest.TestCase):
    file = Path(__file__).parent / "../data/db.sql"
    repo = SmartHouseRepository(file)

    def test_cursor(self):
        c = self.repo.cursor()
        c.execute("SELECT * FROM rooms")
        rooms = c.fetchall()
        self.assertEqual(12, len(rooms))
        c.close()

    # Testing that the device structure is loaded correctly

    def test_basic_no_of_rooms(self):
        h = self.repo.load_smarthouse_deep()
        self.assertEqual(len(h.get_rooms()), 12)

    def test_basic_get_area_size(self):
        h = self.repo.load_smarthouse_deep()
        self.assertEqual(h.get_area(), 156.55)

    def test_basic_get_no_of_devices(self):
        h = self.repo.load_smarthouse_deep()
        self.assertEqual(len(h.get_devices()), 14)


    def test_basic_read_values(self):
        h = self.repo.load_smarthouse_deep()
        actuator = h.get_device_by_id("9a54c1ec-0cb5-45a7-b20d-2a7349f1b132")
        co2_sensor = h.get_device_by_id("8a43b2d7-e8d3-4f3d-b832-7dbf37bf629e")
        amp_sensor = h.get_device_by_id("a2f8690f-2b3a-43cd-90b8-9deea98b42a7")
        humidity_sensor = h.get_device_by_id("3d87e5c0-8716-4b0b-9c67-087eaaed7b45")
        heat_pump = h.get_device_by_id("5e13cabc-5c58-4bb3-82a2-3039e4480a6d")
        # is not even a sensor
        self.assertEqual(None, self.repo.get_latest_reading(actuator))
        # data exists
        self.assertEqual(13.7, self.repo.get_latest_reading(amp_sensor).value)
        self.assertEqual('2024-01-28 23:00:00', self.repo.get_latest_reading(amp_sensor).timestamp)
        # has no data
        self.assertEqual(None, self.repo.get_latest_reading(co2_sensor))
        # data exists
        self.assertEqual(55.2125, self.repo.get_latest_reading(humidity_sensor).value)
        self.assertEqual('2024-01-29 16:00:01', self.repo.get_latest_reading(amp_sensor).timestamp)


    def test_intermediate_save_actuator_state(self):
        h = self.repo.load_smarthouse_deep()
        oven = h.get_device_by_id("8d4e4c98-21a9-4d1e-bf18-523285ad90f6")
        plug = h.get_device_by_id("1a66c3d6-22b2-446e-bf5c-eb5b9d1a8c79")
        oven.turn_on(24.0)
        plug.turn_on()
        self.assertTrue(oven.is_active())
        self.assertTrue(plug.is_acttive())
        # first reconnect
        self.repo.reconnect()
        h = self.repo.load_smarthouse_deep()
        oven = h.get_device_by_id("8d4e4c98-21a9-4d1e-bf18-523285ad90f6")
        plug = h.get_device_by_id("1a66c3d6-22b2-446e-bf5c-eb5b9d1a8c79")
        # activation should have been persisted
        self.assertTrue(oven.is_active())
        self.assertTrue(plug.is_acttive())
        oven.turn_off()
        plug.turn_off()
        self.assertFalse(oven.is_active())
        self.assertFalse(plug.is_acttive())
        # second reconnect
        self.repo.reconnect()
        h = self.repo.load_smarthouse_deep()
        oven = h.get_device_by_id("8d4e4c98-21a9-4d1e-bf18-523285ad90f6")
        plug = h.get_device_by_id("1a66c3d6-22b2-446e-bf5c-eb5b9d1a8c79")
        # deactivation should have been persisted
        self.assertFalse(oven.is_active())
        self.assertFalse(plug.is_acttive())
        
        
    def test_zadvanced_test_humidity_hours(self):
        pass

    def test_zadvanced_test_temp_avgs(self):
        pass
 





if __name__ == '__main__':
    unittest.main()

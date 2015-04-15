import random
from TrackerDash.lib.communicator import Communicator
import time



global TOTAL_PHONES, TOTAL_PRODUCT_A, TOTAL_PRODUCT_B, TOTAL_PRODUCT_C
TOTAL_PHONES = 300
TOTAL_PRODUCT_A = 30
TOTAL_PRODUCT_B = 30
TOTAL_PRODUCT_C = 70


TOTAL__PHONES = 300
TOTAL__PRODUCT_A = 30
TOTAL__PRODUCT_B = 30
TOTAL__PRODUCT_C = 70


def post_data_to_datasources(tests):
    global TOTAL_PHONES, TOTAL_PRODUCT_A, TOTAL_PRODUCT_B, TOTAL_PRODUCT_C

    COMM = Communicator('localhost', 8090)
    tests_running = 0
    tests_in_queue = 0

    for test in tests:
        if test.started == False and test.finished == False:
            tests_in_queue += 1
        if test.running == True:
            tests_running += 1

    running_data = {"Running": tests_running, "In Queue": tests_in_queue}

    COMM.post_data_to_data_source("TestRunData", running_data)

    COMM.post_data_to_data_source("TestKitData", {
            "Phones Available": TOTAL_PHONES,
            "Product A Available": TOTAL_PRODUCT_A,
            "Product B Available": TOTAL_PRODUCT_B,
            "Product C Available": TOTAL_PRODUCT_C
        })


class Test(object):

    def __init__(self, phones=0, _a=0, _b=0, _c=0, cycles=10):
        self.started = False
        self.running = False
        self.finished = False
        self.phones = phones
        self.product_a = _a
        self.product_b = _b
        self.product_c = _c
        self.cycles_run = 0
        self.end_cycle = cycles

    def can_start(self):
        global TOTAL_PHONES, TOTAL_PRODUCT_A, TOTAL_PRODUCT_B, TOTAL_PRODUCT_C

        if not self.started:
            if ((
                    TOTAL_PHONES >= self.phones) and (
                    TOTAL_PRODUCT_A >= self.product_a) and (
                    TOTAL_PRODUCT_B >= self.product_b) and (
                    TOTAL_PRODUCT_C >= self.product_c)):

                return True

    def reserve_and_run(self):
        global TOTAL_PHONES, TOTAL_PRODUCT_A, TOTAL_PRODUCT_B, TOTAL_PRODUCT_C

        TOTAL_PHONES -= self.phones
        TOTAL_PRODUCT_A -= self.product_a
        TOTAL_PRODUCT_B -= self.product_b
        TOTAL_PRODUCT_C -= self.product_c

        self.started = True
        self.running = True

    def run_cycle(self):
        self.cycles_run += 1
        if self.cycles_run >= self.end_cycle:
            self.finished = True
            self.running = False

        self.release_kit()

    def release_kit(self):
        global TOTAL_PHONES, TOTAL_PRODUCT_A, TOTAL_PRODUCT_B, TOTAL_PRODUCT_C

        TOTAL_PHONES += self.phones
        TOTAL_PRODUCT_A += self.product_a
        TOTAL_PRODUCT_B += self.product_b
        TOTAL_PRODUCT_C += self.product_c

def create_graphs():
    COMM = Communicator('localhost', 8090)
    COMM.create_new_graph(
        {
            "title": "Test Run Plan",
            "data_source": "TestRunData",
            "description": "Showing Test Currently Loaded Into Test Runner",
            "data_range": {"days": 1},
            "graph_type": "area",
            "stacked": True
        }
    )
    COMM.create_new_graph(
        {
            "title": "Test Kit Data",
            "data_source": "TestKitData",
            "description": "Showing Total Available Kit In Test Pool",
            "data_range": {"days": 1},
            "graph_type": "area",
            "stacked": True
        }
    )
    COMM.create_new_dashboard(
        {
            "title": "Test Run Statistics",
            "row_data": [
                [
                    {
                        "title": "Test Kit Data",
                        "dimensions": {"width": 12, "height": 1}
                    },
                ],[
                    {
                        "title": "Test Run Plan",
                        "dimensions": {"width": 12, "height": 1}
                    }
                ],
            ]
        }
    )

if __name__ == '__main__':
    create_graphs()

    TESTS = []

    while True:
        print '.'
        new_p = random.randrange(TOTAL__PHONES)
        new_a = random.randrange(TOTAL__PRODUCT_A)
        new_b = random.randrange(TOTAL__PRODUCT_B)
        new_c = random.randrange(TOTAL__PRODUCT_C)
        cycles = random.randrange(10)
        new_test = Test(new_p, new_a, new_b, new_c, cycles)

        TESTS.append(new_test)

        for test in TESTS:
            if test.can_start():
                test.reserve_and_run()
            if test.running:
                test.run_cycle()

        post_data_to_datasources(TESTS)
        time.sleep(2)

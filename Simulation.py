import matplotlib.pyplot as plt
import concurrent.futures
import subprocess
import time


class Simulation:
    def __init__(self,num_clients: list[int], file_name: str):
        self.__num_clients = num_clients
        self.__file_name = file_name

    def run(self)-> list[float]:
        throughput: list[float] = []
        pointer = 0
        for i in self.__num_clients:
            start = time.time_ns()
            for _ in range(10):
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    futures = [executor.submit(self.run_client) for _ in range(i)]

                    for future in concurrent.futures.as_completed(futures):
                        future.result()

            end = ((time.time_ns() - start) / 10) / 1_000_000_000
            throughput.append ((6 * i) / end)
        return throughput

    def draw(self, throughput: list[float]):
        plt.plot(self.__num_clients, throughput, marker = 'o')
        plt.xlabel("Number of clients")
        plt.ylabel("Server throughput (requests / second)")
        plt.plot()

    def run_client(self):
        subprocess.run(["python", self.__file_name, '127.0.0.1', '8080'])

# Run multiple clients in parallel
if __name__ == "__main__":
    sim = Simulation([10, 20, 50], 'Client_Side.py')
    average_throughput = sim.run()
    sim.draw(average_throughput)




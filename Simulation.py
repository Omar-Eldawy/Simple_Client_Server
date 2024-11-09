import matplotlib.pyplot as plt
import concurrent.futures
import subprocess
import time


class Simulation:
    def __init__(self,num_clients: list[int], file_name: str):
        self.__num_clients = num_clients
        self.__file_name = file_name
        self.__num_commands = 6

    def run(self)-> list[float]:
        throughput: list[float] = []
        number_of_simulations = 3
        for i in self.__num_clients:
            start = time.time_ns()
            for _ in range(number_of_simulations):
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    futures = [executor.submit(self.run_client) for _ in range(i)]

                    for future in concurrent.futures.as_completed(futures):
                        future.result()

            end = ((time.time_ns() - start) / number_of_simulations) / 1_000_000_000
            throughput.append ((self.__num_commands * i) / end)
        return throughput

    def draw(self, throughput: list[float]):
        plt.plot([num * self.__num_commands for num in self.__num_clients], throughput, marker = 'o')
        plt.xlabel("Number of requests")
        plt.ylabel("Server throughput (handled requests / second)")
        plt.title("Server throughput vs Number of requests")
        plt.show()

    def run_client(self):
        subprocess.run(["python", self.__file_name, '127.0.0.1', '8080'])

# Run multiple clients in parallel
# To run this file you need to comment the line reading the command line arguments in the Client_Side.py file
# and change the self.__num_commands in the Simulation.py file to the number of commands in your commands file
if __name__ == "__main__":
    sim = Simulation([1, 3, 5, 7, 10, 15, 20, 25, 30, 50, 100, 200,400, 500,800, 1000], 'Simulation_Client.py')
    average_throughput = sim.run()
    sim.draw(average_throughput)




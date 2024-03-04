import simpy
import numpy as np

np.random.seed(10)
tempProcesos = []
intervalos=10

class Proceso:
    def __init__(self, name, env, ram, cpu):
        self.tiempoPromedio = 0
        self.name = name
        self.instrucciones = np.random.randint(1, 11)  # Número de instrucciones que el proceso tiene que ejecutar
        self.memoria = np.random.randint(1, 11)  # Requerimiento de memoria del proceso
        self.hora_inicio = 0
        self.hora_fin = 0
        self.env = env
        self.ram = ram
        self.cpu = cpu

    def run(self):
        print(f"{self.env.now}: Inicia proceso {self.name}, Tareas: {self.instrucciones} restantes")
        self.hora_inicio=self.env.now
        # Solicita la memoria RAM necesaria para el proceso
        with self.ram.get(self.memoria) as req_memoria:
            yield req_memoria

            print(f"{self.env.now}: {self.name} - Esperando por memoria.")

            # Solicita el acceso a la CPU
            with self.cpu.request() as req_cpu:
                yield req_cpu

                # Ejecución de las instrucciones en bloques de 3/6
                while self.instrucciones > 0:
                    instrucciones_ejecutadas = min(6, self.instrucciones)
                    self.instrucciones -= instrucciones_ejecutadas
                    yield self.env.timeout(1)  # Tiempo simulado para ejecutar las instrucciones
                    print(f"{self.env.now}: {self.name} - Ejecutando {instrucciones_ejecutadas} instrucciones. Instrucciones restantes: {self.instrucciones}")
                    # Terminar el proceso si quedan menos de 3 instrucciones
                    if self.instrucciones < 3:
                        self.instrucciones = 0
                        break
                # Simula la posibilidad de una operación de entrada/salida (I/O)
                io_chance = np.random.randint(1, 2)

                if io_chance == 1 and self.instrucciones <= 0:
                    print(f"{self.env.now}: {self.name} - En espera de I/O.")
                    yield self.env.timeout(np.random.randint(1, 2))  # Tiempo simulado de espera para I/O
                    print(f"{self.env.now}: {self.name} - Regresa a ready.")
                else:
                    print(f"{self.env.now}: {self.name} - Termina ejecución.")
            
        
        # Libera la memoria RAM utilizada por el proceso
        
        self.ram.put(self.memoria)
        # Registra el tiempo de finalización del proceso y calcula el tiempo neto
        self.hora_fin = self.env.now
        self.tiempoNeto = int(self.hora_fin - self.hora_inicio)
        tempProcesos.append(self.tiempoNeto)

        print(f"{self.env.now}: {self.name} - Termina proceso. Tiempo neto de: {self.tiempoNeto}")


def crear_procesos(env, ram, cpu, max_num=200, freq=10):
    for i in range(max_num):
        yield env.timeout(freq)
        env.process(Proceso(name=f"Proceso-{i}", env=env, ram=ram, cpu=cpu).run())


def Promedio(lista):
    return sum(lista) / len(lista)

# Simulación

env = simpy.Environment()
RAM = simpy.Container(env, init=200, capacity=200)
CPU = simpy.Resource(env, capacity=2)

env.process(crear_procesos(env, RAM, CPU))
env.run()


tiempoPromedio = Promedio(tempProcesos)
media = np.mean(tempProcesos)
diferencias_cuadraticas = (tempProcesos - media) ** 2
varianza = np.mean(diferencias_cuadraticas)
desviacion_estandar = np.sqrt(varianza)

print("El promedio de tiempo es de: ", tiempoPromedio, ", su desviacion estandar es de: ", desviacion_estandar)

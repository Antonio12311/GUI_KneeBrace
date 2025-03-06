def animation_on_write_serial(self):
    self.combobox.config(state="disabled")
    self.start_animation()
    time.sleep(0.10)
    self.turn_on_motor()
    time.sleep(0.10)

    # Start the send_value function in a separate thread
    self.send_value_running = True
    self.max_torque_reached = False
    self.send_value_thread = threading.Thread(target=self.send_value)
    self.send_value_thread.start()

def toggle_boton(self):
    if self.boton_toggle["text"] == "Iniciar":
        messagebox.showinfo("Estudio", "Se ha comenzado a aplicar fuerza!")
        self.animation_on_write_serial()
        self.boton_toggle.config(text="Detener", image=self.imagen_detener, command=self.toggle_boton)
    else:
        self.animation_off_write_serial()
        self.stop_timer()
        self.label_timer.config(text="00:00")
        self.boton_toggle.config(text="Iniciar", image=self.imagen_iniciar, command=self.toggle_boton)

        # Stop the send_value loop
        self.send_value_running = False
        if self.send_value_thread is not None:
            self.send_value_thread.join()  # Wait for the thread to finish
            self.send_value_thread = None

        # Turn off the motor only when the user presses the stop button
        self.turn_off_motor()

    if self.level.startswith("Nivel "):
        level_num = int(self.level.split(" ")[1])
        self.squares[level_num].config(bg="#FFFFFF")

def send_value(self):
    cadena = str(self.combobox.get())
    nivel = int(cadena.split()[1])
    divided_value = nivel / 4
    cumulative_value = 0

    while self.send_value_running and cumulative_value < nivel:
        cumulative_value += divided_value
        if self.ser and self.ser.is_open:  # Ensure the serial port is open
            self.arduino_lock.acquire()  # Acquire the lock for thread-safe access
            try:
                self.ser.write((str(cumulative_value) + "\n").encode('ascii'))  # Send the cumulative value
                print(f"Sent: {cumulative_value}")  # Debug print
            except Exception as e:
                print(f"Error writing to serial port: {e}")
            finally:
                self.arduino_lock.release()  # Release the lock
        else:
            print("Serial port is not open.")
            break

        time.sleep(2)  # Wait for 2 seconds before the next iteration

    # When max torque is reached
    if cumulative_value >= nivel:
        self.max_torque_reached = True
        messagebox.showinfo("Alerta", "Se ha alcanzado el torque máximo.")
        self.start_timer()  # Start the countdown timer
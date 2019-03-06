#!/bin/python
import os           # Used for basename
import subprocess   # Used for executing command
import logging      # Used for logging
import sys          # Used to configure logging
import time         # Used for sleep, time, and strftime


class Nstat:
    CMD = 'nstat'
    ALL = '-a'
    JSON = '-j'
    NO_UPDATE = '-s'
    RESET = '-n'


class NstatCollector:

    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, 'a')

    def __del__(self):
        self.file.close()

    # Execute 'nstat' and write to file
    def get(self, all_values=False, json=True, no_update=True, reset_history=False):
        time_string = ""
        # Create command
        cmd = [Nstat.CMD]
        # Check reset_history first, as it eclipses all other values
        if reset_history:
            cmd.extend([Nstat.RESET])
        else:  # Only extend other values if rest_history is false
            if all_values:
                cmd.extend([Nstat.ALL])
            if json:
                cmd.extend([Nstat.JSON])
            if no_update:
                cmd.extend([Nstat.NO_UPDATE])
            # Get timestamp
            time_string = "{\"time\":" + str(time.time()) + "}"

        # Log timestamp for complete debug log
        logging.debug("Timestamp before cmd:\n\t%s", time_string)
        # Get command result
        result = self.execute_command(cmd)
        # Write result to file
        self.file.writelines([time_string, result])

    def run(self, reset_history=False):
        if reset_history:
            self.get(reset_history=reset_history)
        # Set running flag and begin looping
        running = True
        while running:
            try:
                self.get()
                time.sleep(1)
            except KeyboardInterrupt:  # Catch CTRL-C
                logging.debug("User keyboard interrupt caught")
                # Todo: Perform processing in future?
                logging.info("Perform processing in future?")
                # Raise flag and exit
                print("Exiting from run loop.")
                running = False

    @staticmethod
    def execute_command(cmd):
        logging.debug('Running cmd (%s).', cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
        # Log command to debug
        logging.debug("Result from cmd (%s): \n\t%s", cmd, result)
        return result


def main():
    print("Starting to run script: %s", os.path.basename(__file__))

    # Configure logger to put debug into stderr
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    # Create file name for logging
    file_name = "nstat-" + time.strftime("%Y_%m_%d-%H_%M_%S") + ".log"
    # Log the file name
    print("Beginning to collect data, using cmd (%s), to file (%s).", Nstat.CMD, file_name)
    # Create new collector
    collector = NstatCollector(file_name)
    # Run the collector
    collector.run(reset_history=True)

    print("Done running.")


if __name__ == '__main__':
    main()

# STEP BY STEP TUTORIAL:
## How to run this project

1. Download the recommended Mininet VM image from [Mininet's Github](https://github.com/mininet/mininet/releases/).

2. Run the following commands:
    ```bash
    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ sudo apt install docker.io
    $ sudo apt install docker-compose-v2
    ```

3. Clone our repository into the VM:
    ```bash
    $ git clone https://github.com/jrpfaria/CM.git
    ```

4. Setup the docker container:
    ```bash
    $ sudo docker compose -d
    ```

5. Run the mininet configuration:
    ```bash
    sudo python3 network.py
    ```

## How to edit this project
- If you change Faucet's configuration, run the following command to trigger the changes:
    ```bash
    $ sudo docker exec -it faucet sh
    $ pkill -HUP -f faucet.faucet
    ```

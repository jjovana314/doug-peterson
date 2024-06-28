# Doug Peterson

Doug Peterson is a Discord bot designed to monitor users' activity on a server and assign roles based on their activity or inactivity. Additionally, Doug Peterson responds to users' messages with quotes from the TV show 'What We Do in the Shadows'.

## Features

- **Activity Monitoring**: Doug Peterson monitors users' activity on the server.
- **Role Assignment**: Based on users' activity or inactivity, Doug Peterson assigns roles accordingly.
- **Quote Responses**: Responds to users' messages with quotes from the TV show 'What We Do in the Shadows'.
- **Customizable Settings**: Configure Doug Peterson's behavior through customizable settings.

## Installation and configuration

1. Clone this repository:

   ```bash
   git clone https://github.com/your_username/doug-peterson.git
   ```
   
2. Navigate to project directory:

    ```bash
    cd doug-peterson
    ```

3. Install the required dependencies:

    ```bash
   pip install -r requirements.txt
    ```

4. Create a .env file in the project directory and add your Discord bot token:

    ```bash
    TOKEN=your_discord_token_here
    CHANNEL_ID=your_channel_id_here
    LURKER_ROLE_ID=your_lurker_role_id_here
    TRUST_ROLE_ID=your_trust_role_id_here
    BOTS_ROLE_ID=your_bots_role_id_here
    ESCAPE_LURKER_ROLE_ID=your_escape_lurker_role_id_here
    REDIS_URL=your_redis_url_here
   ```
    Explanation of each variable:
    - **TOKEN**: Your Discord bot token obtained from the Discord Developer Portal.
    - **CHANNEL_ID**: The ID of the channel where Doug Peterson will operate.
    - **LURKER_ROLE_ID**: The role ID assigned to lurkers (users who are inactive for a certain period).
    - **TRUST_ROLE_ID**: The role ID assigned to trusted users (active users).
    - **BOTS_ROLE_ID**: The role ID assigned to bots.
    - **ESCAPE_LURKER_ROLE_ID**: The role ID for users who escape from the lurker role.
    - **REDIS_URL**: The URL for the Redis database used for data storage.


5. Run the bot

    ```bash
   python main.py
   ```

## Usage

Add Doug Peterson to your discord server and assign admin role to bot (bot needs to have full access). After that, use
command ```!check_lurker``` and bot will automatically check all users in order to find lurkers. If bot finds inactive
users - he'll assign them lurker role.

## Contributing

Contributions are welcome! If you'd like to contribute to Doug Peterson, feel free to fork this repository and submit a pull request.
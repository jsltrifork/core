from aiohttp import ClientSession, BasicAuth
import asyncio


async def get_sensor_info(sia_url: str, username: str, password: str):
    """Gets sensor info from SIA"""

    auth = BasicAuth(username, password=password)
    url = f"http://{sia_url}/api/init"

    async with ClientSession(auth=auth) as session:
        async with session.get(url) as resp:
            json = await resp.json()

    sensors = []

    for plugin in json["plugins"]:
        plugin_name = plugin["name"]
        print(plugin_name)
        print(len(plugin["devices"]))

        for device in plugin["devices"]:
            device_id = device["id"]
            print(plugin_name)
            print(len(device["items"]))
            for item in device["items"]:
                sensors.append(
                    {
                        "id": item["id"],
                        "plugin": plugin_name,
                        "device_id": device_id,
                        "unit": item["unit"],
                        "name": item["name"],
                    }
                )
    return sensors


async def test_json():
    url = "172.31.100.129"  # user_input[CONF_URL]
    username = "Trifork"  # user_input[CONF_USERNAME]
    password = "Trifork"  # user_input[CONF_PASSWORD]

    sensors = await get_sensor_info(url, username, password)


if __name__ == "__main__":
    asyncio.run(test_json())


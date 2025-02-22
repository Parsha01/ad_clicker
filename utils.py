"""
HAYAT BÖYLE ZATEN

Bu evin bir köpeği vardı;
Kıvır kıvırdı, adı Çinçon'du, öldü.
Bir de kedisi vardı: Maviş,
Kayboldu.
Evin kızı gelin oldu,
Küçük Bey sınıfı geçti.
Daha böyle acı, tatlı
Neler oldu bir yıl içinde!
Oldu ya, olanların hepsi böyle...
Hayat böyle zaten!..

                        -- Orhan Veli
"""

import sys
import random
import subprocess
from pathlib import Path
from time import sleep
from typing import Optional

import requests
import undetected_chromedriver

from config import logger
from geolocation_db import GeolocationDB
from proxy import install_plugin


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.101 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.101 Mobile/15E148 Safari/604.1",
]


def get_random_user_agent_string() -> str:
    """Get random user agent

    :rtype: str
    :returns: User agent string
    """

    user_agent_string = random.choice(USER_AGENTS)

    logger.debug(f"user_agent: {user_agent_string}")

    return user_agent_string


def get_location(
    geolocation_db_client: GeolocationDB, proxy: str, auth: Optional[bool] = False
) -> tuple[float, float]:
    """Get latitude and longitude of ip address

    :type geolocation_db_client: GeolocationDB
    :param geolocation_db_client: GeolocationDB instance
    :type proxy: str
    :param proxy: Proxy to get geolocation
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    :rtype: tuple
    :returns: (latitude, longitude) pair for the given proxy IP
    """

    proxies_header = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    if auth:
        for _ in range(2):
            try:
                response = requests.get(
                    "https://ipv4.webshare.io/", proxies=proxies_header, timeout=5
                )
                ip_address = response.text
                break

            except:
                try:
                    response = requests.get(
                        "https://ifconfig.co/json", proxies=proxies_header, timeout=5
                    )
                    ip_address = response.json().get("ip")
                    break

                except:
                    logger.debug("Request will be resend after 60 seconds")
                    sleep(60)
    else:
        ip_address = proxy.split(":")[0]

    logger.info(f"Connecting with IP: {ip_address}")

    db_result = geolocation_db_client.query_geolocation(ip_address)

    latitude = None
    longitude = None

    if db_result:
        latitude, longitude = db_result
        logger.debug(f"Cached latitude and longitude for {ip_address}: ({latitude}, {longitude})")

        return float(latitude), float(longitude)

    else:
        retry_count = 0
        max_retry_count = 5
        sleep_seconds = 5

        while retry_count < max_retry_count:
            try:
                response = requests.get(
                    f"https://ipapi.co/{ip_address}/json/", proxies=proxies_header, timeout=5
                )
                latitude, longitude = (
                    response.json().get("latitude"),
                    response.json().get("longitude"),
                )
                break
            except Exception as exp:
                logger.debug(exp)
                logger.debug("Continue with ifconfig.co")

                try:
                    response = requests.get(
                        "https://ifconfig.co/json", proxies=proxies_header, timeout=5
                    )
                    latitude, longitude = (
                        response.json().get("latitude"),
                        response.json().get("longitude"),
                    )
                    break
                except Exception as exp:
                    logger.debug(exp)
                    logger.debug("Continue with ipconfig.io")

                    try:
                        response = requests.get(
                            "https://ipconfig.io/json/", proxies=proxies_header, timeout=5
                        )
                        latitude, longitude = (
                            response.json()["latitude"],
                            response.json()["longitude"],
                        )
                        break
                    except Exception as exp:
                        logger.debug(exp)
                        logger.error(
                            f"Couldn't find latitude and longitude for {ip_address}! "
                            f"Retrying after {sleep_seconds} seconds..."
                        )

                        retry_count += 1
                        sleep(sleep_seconds)
                        sleep_seconds *= 2

        if latitude and longitude:
            logger.debug(f"Latitude and longitude for {ip_address}: ({latitude}, {longitude})")
            geolocation_db_client.save_geolocation(ip_address, latitude, longitude)

            return (latitude, longitude)
        else:
            return (None, None)


def get_installed_chrome_version() -> int:
    """Get major version for the Chrome installed on the system

    :rtype: int
    :returns: Chrome major version
    """

    major_version = None

    try:
        if sys.platform == "win32":
            chrome_exe_path = undetected_chromedriver.find_chrome_executable()
            version_command = (
                f"wmic datafile where name='{chrome_exe_path}' get Version /value".replace(
                    "\\", "\\\\"
                )
            )
            chrome_version = subprocess.check_output(version_command, shell=True)
            major_version = int(chrome_version.decode("utf-8").strip().split(".")[0].split("=")[1])

        elif sys.platform == "darwin":
            chrome_version = subprocess.run(
                "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version",
                shell=True,
                capture_output=True,
            )
            major_version = int(chrome_version.stdout.decode("utf-8").split()[-1].split(".")[0])

        else:
            chrome_version = subprocess.run(["google-chrome", "--version"], capture_output=True)
            major_version = int(str(chrome_version.stdout).split()[-2].split(".")[0])

        logger.debug(f"Installed Chrome version: {major_version}")

    except subprocess.SubprocessError:
        logger.error("Failed to get Chrome version! Latest version will be used.")

    return major_version


def get_queries(query_file: Path) -> list[str]:
    """Get queries from file

    :type query_file: Path
    :param query_file: File containing queries
    :rtype: list
    :returns: List of queries
    """

    filepath = Path(query_file)

    if not filepath.exists():
        raise SystemExit(f"Couldn't find queries file: {filepath}")

    with open(filepath, encoding="utf-8") as queryfile:
        queries = [
            query.strip().replace("'", "").replace('"', "")
            for query in queryfile.read().splitlines()
        ]

    return queries


def create_webdriver(
    proxy: str, auth: bool, headless: bool, incognito: Optional[bool] = False
) -> undetected_chromedriver.Chrome:
    """Create Selenium Chrome webdriver instance

    :type proxy: str
    :param proxy: Proxy to use in ip:port or user:pass@host:port format
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    :type headless: bool
    :param headless: Whether to use headless browser
    :type incognito: bool
    :param incognito: Whether to run in incognito mode
    :rtype: undetected_chromedriver.Chrome
    :returns: Selenium Chrome webdriver instance
    """

    geolocation_db_client = GeolocationDB()

    user_agent_str = get_random_user_agent_string()

    chrome_options = undetected_chromedriver.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-service-autorun")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"--user-agent={user_agent_str}")

    if incognito:
        chrome_options.add_argument("--incognito")

    if headless:
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

    chrome_version = get_installed_chrome_version()

    if proxy:
        logger.info(f"Using proxy: {proxy}")

        if auth:
            if "@" not in proxy or proxy.count(":") != 2:
                raise ValueError(
                    "Invalid proxy format! Should be in 'username:password@host:port' format"
                )

            username, password = proxy.split("@")[0].split(":")
            host, port = proxy.split("@")[1].split(":")

            install_plugin(chrome_options, host, int(port), username, password)

        else:
            chrome_options.add_argument(f"--proxy-server={proxy}")

        driver = undetected_chromedriver.Chrome(
            version_main=chrome_version,
            options=chrome_options,
            headless=headless,
        )

        # set geolocation of the browser according to IP address
        accuracy = 90
        lat, long = get_location(geolocation_db_client, proxy, auth)

        if lat and long:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {"latitude": lat, "longitude": long, "accuracy": accuracy},
            )

            response = requests.get(
                f"http://timezonefinder.michelfe.it/api/0_{long}_{lat}", timeout=5
            )

            if response.status_code == 200:
                timezone = response.json()["tz_name"]
                logger.debug(f"Timezone of {proxy.split('@')[1] if auth else proxy}: {timezone}")
                driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": timezone})

    else:
        driver = undetected_chromedriver.Chrome(
            version_main=chrome_version, options=chrome_options, headless=headless
        )

    return driver

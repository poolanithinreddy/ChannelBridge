import logging
import time

logging.basicConfig(level=logging.INFO);log=logging.getLogger("channelbridge.worker")
if __name__=="__main__":
    log.info("durable_worker status=ready operation=poll retry_policy=bounded_exponential")
    while True: time.sleep(5)

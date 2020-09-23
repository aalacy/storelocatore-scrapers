import time

class ETA:
    """
    A completion estimate utility that depends on pre-existing knowledge of overall things to count,
    and keeps an internal tally of stats to allow for meaningful time estimation.
    Example usage:
    eta = ETA(total_record_count = 1000)
    # .... some init code
    eta.kickoff()
    records = fetch_some_records()
    while records:
      (records_sec, remaining_sec, elapsed_sec, remaining_records, counted_so_far) = eta.update_and_get_stats(len(records))
      # print stats
      # do something with records
      records = fetch_some_records()
    """

    def __init__(self, total_record_count: int):
        """
        :param total_record_count: How many units to be counted overall?
        """
        self.__total_count = total_record_count
        self.__counted_so_far = 0
        self.__stopwatch_sec = 0.0
        self.__elapsed_sec = 0.0

    def kickoff(self) -> None:
        """
        Sets off the internal stopwatch
        """
        self.__stopwatch_sec = time.clock_gettime(0)

    def update_and_get_stats(self, added: int) -> (float, float, float, int, float):
        """
        Adds the number of counted records to the aggregate, and returns the current stats.
        :param added: How many items were counted in the current iteration?
        :return: A 5-tuple, (records/sec, remaining_sec, elapsed_sec, remaining_records, counted so far)
        """

        now_sec = time.clock_gettime(0)
        step_took_sec = now_sec - self.__stopwatch_sec
        self.__stopwatch_sec = now_sec
        self.__elapsed_sec += step_took_sec
        self.__counted_so_far += added

        records_per_sec = self.__counted_so_far / self.__elapsed_sec
        remaining_recs = self.__total_count - self.__counted_so_far
        remaining_sec = remaining_recs / records_per_sec

        return records_per_sec, remaining_sec, self.__elapsed_sec, remaining_recs, self.__counted_so_far, step_took_sec


def __test():
    eta = ETA(total_record_count=10)
    eta.kickoff()

    for i in range(0,11): # overshoot for good measure!
        time.sleep(1)
        (rps, rs, es, rr, csf) = eta.update_and_get_stats(1)
        print(f"rec/s {rps}, remaining sec {rs}, elapsed sec {es}, remaining rec {rr}, counted so far {csf}")

def listen_to_file(filepath: string):
    pass




if __name__ == "__main__":
    __test()
import random

class ActivitySimulator:
    def __init__(self, workday_minutes=480, interval_duration=60):
        self.workday_minutes = workday_minutes
        self.interval_duration = interval_duration

    def simulate_usage_time(self):
        usage_data = []
        remaining_time = self.workday_minutes

        while remaining_time > 0:
            activity_duration = min(random.randint(10, self.interval_duration), remaining_time)
            usage_data.append(activity_duration)
            remaining_time -= activity_duration + 1

        return usage_data

    def simulate_inactivity(self, usage_data):
        inactivity_data = []

        for duration in usage_data:
            inactivity_duration = random.randint(0, duration // 2)
            inactivity_data.append(inactivity_duration)

        return inactivity_data

    def simulate_activity_labels(self, inactivity_data, activity_data, threshold_ratio=0.15, activity_threshold=30):
        activity_labels = []

        for inactivity_duration, activity_duration in zip(inactivity_data, activity_data):
            if activity_duration > activity_threshold and activity_duration > 0 and (inactivity_duration / activity_duration) <= threshold_ratio:
                activity_labels.append("break needed")
            else:
                activity_labels.append("no break needed")

        return activity_labels

    def simulate_data(self):
        usage_data = self.simulate_usage_time()
        inactivity_data = self.simulate_inactivity(usage_data)
        activity_labels = self.simulate_activity_labels(inactivity_data, usage_data)
        return usage_data, inactivity_data, activity_labels

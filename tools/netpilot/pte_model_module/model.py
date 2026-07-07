class ForecastModel:
    def fit(self, history):
        pass

    def predict(self, series, horizon):
        return [{"t": i, "value": v} for i, v in enumerate(series[-horizon:])]

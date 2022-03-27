import numpy
from pysofar.wavespectra.tools import to_datetime, datetime_to_iso_time_string
from typing import TypedDict, List

class WaveSpectrumInput(TypedDict):
    frequency: List[float]
    varianceDensity: List
    timestamp: str
    latitude: float
    longitude: float

class WaveSpectrum():
    """
    Base spectral class.
    """
    frequency_units = 'Hertz'
    angular_units = 'Degrees'
    spectral_density_units = 'm**2/Hertz'
    angular_convention = 'Wave travel direction (going-to), measured anti-clockwise from East'

    def __init__(self,
                 wave_spectrum_input: WaveSpectrumInput
                 ):

        self.frequency = numpy.array(wave_spectrum_input['frequency'])
        self.variance_density = numpy.array(wave_spectrum_input['varianceDensity'])
        self.direction = None
        self._a1 = None
        self._b1 = None
        self._a2 = None
        self._b2 = None
        self._e = None
        self.timestamp = to_datetime(wave_spectrum_input['timestamp'])
        self.longitude = wave_spectrum_input['longitude']
        self.latitude = wave_spectrum_input['latitude']

    def frequency_moment(self, power: int, fmin=0, fmax=numpy.inf) -> float:
        pass

    def _create_wave_spectrum_input(self)->WaveSpectrumInput:
        return WaveSpectrumInput(
            frequency=list(self.frequency),
            varianceDensity=list(self.variance_density),
            timestamp=datetime_to_iso_time_string(self.timestamp),
            latitude=self.latitude,
            longitude=self.longitude
        )

    def _range(self, fmin=0.0, fmax=numpy.inf)->numpy.ndarray:
        return (self.frequency >= fmin) & (self.frequency < fmax)

    @property
    def radian_direction(self) -> numpy.ndarray:
        return self.direction * numpy.pi / 180

    @property
    def radian_frequency(self) -> numpy.ndarray:
        return self.frequency * 2 * numpy.pi

    @property
    def e(self) -> numpy.array:
        return self._e

    @property
    def a1(self) -> numpy.array:
        return self._a1

    @property
    def b1(self) -> numpy.array:
        return self._b1

    @property
    def a2(self) -> numpy.array:
        return self._a2

    @property
    def b2(self) -> numpy.array:
        return self._b2

    @property
    def A1(self) -> numpy.array:
        return self.a1 * self.e

    @property
    def B1(self) -> numpy.array:
        return self.b1 * self.e

    @property
    def A2(self) -> numpy.array:
        return self.a2 * self.e

    @property
    def B2(self) -> numpy.array:
        return self.b2 * self.e

    def m0(self, fmin=0, fmax=numpy.inf) -> float:
        return self.frequency_moment(0, fmin, fmax)

    def m1(self, fmin=0, fmax=numpy.inf) -> float:
        return self.frequency_moment(1, fmin, fmax)

    def m2(self, fmin=0, fmax=numpy.inf) -> float:
        return self.frequency_moment(2, fmin, fmax)

    def hm0(self, fmin=0, fmax=numpy.inf) -> float:
        return 4 * numpy.sqrt(self.m0(fmin, fmax))

    def tm01(self, fmin=0, fmax=numpy.inf) -> float:
        return self.m0(fmin, fmax) / self.m1(fmin, fmax)

    def tm02(self, fmin=0, fmax=numpy.inf) -> float:
        return numpy.sqrt(self.m0(fmin, fmax) / self.m2(fmin, fmax))

    def peak_index(self, fmin=0, fmax=numpy.inf) -> float:
        range = self._range(fmin, fmax)

        return numpy.argmax(self.e[range])

    def peak_frequency(self, fmin=0, fmax=numpy.inf) -> float:
        return self.frequency[self.peak_index(fmin, fmax)]

    def peak_period(self, fmin=0, fmax=numpy.inf) -> float:
        return 1 / self.peak_frequency(fmin, fmax)

    def peak_direction(self, fmin=0, fmax=numpy.inf):
        index = self.peak_index(fmin, fmax)
        a1 = self.a1[index]
        b1 = self.b1[index]
        return self._mean_direction(a1, b1)

    def peak_spread(self, fmin=0, fmax=numpy.inf):
        index = self.peak_index(fmin, fmax)
        a1 = self.a1[index]
        b1 = self.b1[index]
        return self._spread(a1, b1)

    @staticmethod
    def _mean_direction(a1, b1):
        return numpy.arctan2(b1, a1) * 180 / numpy.pi

    @staticmethod
    def _spread(a1, b1):
        return numpy.sqrt(
            2 - 2 * numpy.sqrt(a1 ** 2 + b1 ** 2)) * 180 / numpy.pi

    @property
    def mean_direction(self):
        return self._mean_direction(self.a1, self.b1)

    @property
    def mean_spread(self):
        return self._spread(self.a1, self.b1)

    def _spectral_weighted(self, property, fmin=0, fmax=numpy.inf):
        range = (self._range(fmin,fmax)) & numpy.isfinite( property )

        return numpy.trapz(property[range] * self.e[range],
                           self.frequency[range]) / self.m0(fmin, fmax)

    def bulk_direction(self, fmin=0, fmax=numpy.inf):
        return self._mean_direction(self.bulk_a1(fmin, fmax),
                                    self.bulk_b1(fmin, fmax))

    def bulk_spread(self, fmin=0, fmax=numpy.inf):
        return self._spread(self.bulk_a1(fmin, fmax), self.bulk_b1(fmin, fmax))

    def bulk_a1(self, fmin=0, fmax=numpy.inf):
        return self._spectral_weighted(self.a1, fmin, fmax)

    def bulk_b1(self, fmin=0, fmax=numpy.inf):
        return self._spectral_weighted(self.b1, fmin, fmax)

    def bulk_a2(self, fmin=0, fmax=numpy.inf):
        return self._spectral_weighted(self.a2, fmin, fmax)

    def bulk_b2(self, fmin=0, fmax=numpy.inf):
        return self._spectral_weighted(self.b2, fmin, fmax)
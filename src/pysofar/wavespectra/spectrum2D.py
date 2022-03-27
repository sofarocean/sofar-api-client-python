import numpy
from .wavespectrum import WaveSpectrum, WaveSpectrumInput
from typing import List, Union
from .tools import datetime_to_iso_time_string


class WaveSpectrum2DInput(WaveSpectrumInput):
    directions: Union[List[float], numpy.ndarray]

class WaveSpectrum2D(WaveSpectrum):
    def __init__(self,
                 wave_spectrum2D_input:WaveSpectrum2DInput
                 ):

        super().__init__(wave_spectrum2D_input)
        self.direction = wave_spectrum2D_input['directions']
        self._a1 = self._directional_moment('a', 1, normalized=True)
        self._b1 = self._directional_moment('b', 1, normalized=True)
        self._a2 = self._directional_moment('a', 2, normalized=True)
        self._b2 = self._directional_moment('b', 2, normalized=True)
        self._e = self._directional_moment('zero', 0, normalized=False)

    def _delta(self):
        angles = self.direction
        forward_diff = (numpy.diff(angles, append=angles[0]) + 180) % 360 - 180
        backward_diff = (numpy.diff(angles,
                                    prepend=angles[-1]) + 180) % 360 - 180
        return (forward_diff + backward_diff) / 2

    def _directional_moment(self, kind='zero', order=0,
                            normalized=True) -> numpy.array:
        delta = self._delta()
        if kind == 'a':
            harmonic = numpy.cos(self.radian_direction * order) * delta
        elif kind == 'b':
            harmonic = numpy.sin(self.radian_direction * order) * delta
        elif kind == 'zero':
            harmonic = delta
        else:
            raise Exception('Unknown moment')
        values = numpy.sum(self.variance_density * harmonic[None, :], axis=-1)

        if normalized:
            scale = numpy.sum(self.variance_density * delta[None, :], axis=-1)
        else:
            scale = 1

        return values / scale

    def frequency_moment(self, power: int, fmin=0, fmax=numpy.inf) -> float:
        range = self._range(fmin, fmax)
        return numpy.trapz(self.e[range] * self.frequency[range] ** power,
                           self.frequency[range])

    def _create_wave_spectrum_input(self)->WaveSpectrum2DInput:
        return WaveSpectrum2DInput(
            frequency=list(self.frequency),
            directions=list(self.direction),
            varianceDensity=list(self.variance_density),
            timestamp=datetime_to_iso_time_string(self.timestamp),
            latitude=self.latitude,
            longitude=self.longitude,
        )
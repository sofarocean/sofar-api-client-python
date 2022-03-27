import numpy
from .spectrum2D import WaveSpectrum2D, WaveSpectrum2DInput
from .wavespectrum import WaveSpectrum, WaveSpectrumInput
from .tools import to_datetime, datetime_to_iso_time_string
from .mem import mem
from typing import List, Union

class WaveSpectrum1DInput(WaveSpectrumInput):
    a1: Union[List[float], numpy.ndarray]
    b1: Union[List[float], numpy.ndarray]
    a2: Union[List[float], numpy.ndarray]
    b2: Union[List[float], numpy.ndarray]

class WaveSpectrum1D(WaveSpectrum):
    spectral_density_units = 'm**2/Hertz'

    def __init__(self,
                 wave_spectrum1D_input:WaveSpectrum1DInput
                 ):
        super().__init__(wave_spectrum1D_input)
        self._a1 = numpy.array(wave_spectrum1D_input['a1'])
        self._b1 = numpy.array(wave_spectrum1D_input['b1'])
        self._b2 = numpy.array(wave_spectrum1D_input['b2'])
        self._a2 = numpy.array(wave_spectrum1D_input['a2'])
        self._e = numpy.array(wave_spectrum1D_input['varianceDensity'])

    def frequency_moment(self, power: int, fmin=0, fmax=numpy.inf) -> float:
        range = self._range(fmin,fmax)

        return numpy.trapz(
            self.variance_density[range] * self.frequency[range] ** power,
            self.frequency[range])

    def _create_wave_spectrum_input(self)->WaveSpectrum1DInput:
        return WaveSpectrum1DInput(
            frequency=list(self.frequency),
            varianceDensity=list(self.variance_density),
            timestamp=datetime_to_iso_time_string(self.timestamp),
            latitude=self.latitude,
            longitude=self.longitude,
            a1=list(self.a1),
            b1=list(self.b1),
            a2=list(self.a2),
            b2=list(self.b2)
            )

    def spectrum2d(self, number_of_directions: int,
                   method:str='maximum_entropy_method')->WaveSpectrum2D:
        """
        Construct a 2D spectrum based on the 1.5D spectrum and a spectral
        reconstruction method.

        :param number_of_directions: length of the directional vector for the
        2D spectrum. Directions returned are in degrees
        """
        direction = numpy.linspace(0, 360, number_of_directions,
                                   endpoint=False)

        # Jacobian to transform distribution as function of radian angles into
        # degrees.
        Jacobian = numpy.pi / 180

        if method.lower() in ['maximum_entropy_method', 'mem']:
            # reconstruct the directional distribution using the maximum entropy
            # method.
            D = mem(direction * numpy.pi / 180, self.a1, self.b1, self.a2,
                    self.b2) * Jacobian
        else:
            raise Exception(f'unsupported spectral estimator method: {method}')

        wave_spectrum2D_input = WaveSpectrum2DInput(
            frequency=self.frequency,
            directions=direction,
            varianceDensity=self.variance_density[:, None] * D,
            timestamp=self.timestamp,
            longitude=self.longitude,
            latitude=self.latitude
        )

        # We return a 2D wave spectrum object.
        return WaveSpectrum2D(wave_spectrum2D_input)



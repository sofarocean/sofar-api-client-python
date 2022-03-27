import numpy

def mem(directions_radians: numpy.ndarray, a1, b1, a2, b2) -> numpy.ndarray:
    """
    This function uses the maximum entropy method by Lygre and Krogstadt (1986,JPO)
    to estimate the directional shape of the spectrum.

    Lygre, A., & Krogstad, H. E. (1986). Maximum entropy estimation of the directional
    distribution in ocean wave spectra. Journal of Physical Oceanography, 16(12), 2052-2060.

    :param direction_radians: radian directions (going to, anti-clockswise from east) want to
                              evaluate the spectrum on
    :param a1: 1st cosine Fourier coefficient of the directional distribution
    :param b1: 1st sine Fourier coefficient of the directional distribution
    :param a2: 2nd cosine Fourier coefficient of the directional distribution
    :param b2: 2nd sine Fourier coefficient of the directional distribution

    :return: Directional distribution as a numpy array

    Note that:
    d1 = a1; d2 =b1; d3 = a2 and d4=b2 in the defining equations 10.
    """

    # Ensure that these are numpy arrays
    a1 = numpy.atleast_1d(a1)
    b1 = numpy.atleast_1d(b1)
    a2 = numpy.atleast_1d(a2)
    b2 = numpy.atleast_1d(b2)

    number_of_directions = len(directions_radians)

    c1 = a1 + 1j * b1
    c2 = a2 + 1j * b2
    #
    # Eq. 13 L&K86
    #
    Phi1 = (c1 - c2 * numpy.conj(c1)) / (1 - c1 * numpy.conj(c1))
    Phi2 = c2 - Phi1 * c1
    #
    e1 = numpy.exp(-directions_radians * 1j)
    e2 = numpy.exp(-directions_radians * 2j)

    numerator = (1 - Phi1 * numpy.conj(c1) - Phi2 * numpy.conj(c2))
    denominator = numpy.abs(1 - Phi1[:,None] * e1[None,:]
                              - Phi2[:,None] * e2[None,:]) ** 2

    D = numpy.real( numerator[:,None] / denominator  ) / numpy.pi / 2

    # Normalize to 1. in discrete sense
    integralApprox = numpy.sum(D,axis=-1) * numpy.pi * 2. / number_of_directions
    D = D / integralApprox[:,None]

    return numpy.squeeze(D)
__all__ = ["MopsObjects"]

class diasource(object):
    def __init__(self, diaid, ssmid, obshistid, ra, dec, mjd, mag, snr):

        self._diaid = diaid
        self._ssmid = ssmid
        self._obshistid = obshistid
        self._ra = ra
        self._dec = dec
        self._mjd = mjd
        self._mag = mag
        self._snr = snr
        
    @property
    def diaid(self):
        return self._diaid

    @diaid.setter
    def diaid(self, value):
        self._diaid = value

    @property
    def ssmid(self):
        return self._ssmid

    @ssmid.setter
    def ssmid(self, value):
        self._ssmid = value

    @property
    def obshistid(self):
        return self._obshistid

    @obshistid.setter
    def obshistid(self, value):
        self._obshistid = value

    @property
    def ra(self):
        return self._ra

    @ra.setter
    def ra(self, value):
        self._ra = value

    @property
    def dec(self):
        return self._dec

    @dec.setter
    def dec(self, value):
        self._dec = value

    @property
    def mjd(self):
        return self._mjd

    @mjd.setter
    def mjd(self, value):
        self._mjd = value

    @property
    def mag(self):
        return self._mag

    @mag.setter
    def mag(self, value):
        self._mag = value

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, value):
        self._snr = value
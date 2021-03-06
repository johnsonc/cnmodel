TITLE ihsgc-basalmiddle.mod - Spiral Ganglion Cell Ih current for basal and middle Regions

COMMENT
Ih for Spiral ganglion cells.
Kinetcs are based on average fits to mouse SGCs,
This model is for the basal and middle cell groups (averaged).
Data used to establish the kinetic parameters were collected by
Qing Liu and Robin Davis (Rutgers).
Data were taken at room temperature.
Kinetic parameters were extracted by curve fitting for fast and
slow components from activation and deactivation (using
the program Ihfit4b.py).

Implementation by Paul B. Manis, January-April, 2012.
Revised December 2013, January 2014.
        # of parameters in the fit were decreased (tau uses one v and scale factor).
Parameters are shown in the tables in Liu et al., JARO 2014.

March 13, 2014: Corrected version with boltzmax for slow component
July 2014: made threadsafe, changed solver

pmanis@med.unc.edu

Note: vshift parameter is nominally 0. This parameter can
shift the entire activation and rate curves, keeping them
in register for each component of the conductance.

ENDCOMMENT

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(nA) = (nanoamp)
}

NEURON {
	THREADSAFE
    SUFFIX ihsgcBasalMiddle
	NONSPECIFIC_CURRENT i
	RANGE gbar, gh, ih, eh, vshift
	RANGE vh, k, vhs, ks
	RANGE rinf, rtau, sinf, stau
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
		v (mV)
		celsius = 22 (degC)
		dt (ms)
		gbar = 0.00318 (mho/cm2) <0,1e9>
        eh = -41 (mV)

: Parameters from kinetic analysis
: Formatted for NEURON MOD file
: (Run on date =  2014-01-01 12:52:22.776598 )

: lmfit, Constrained model t(v) = DC + 1/(a * exp((v+vh)/k1) + a*exp(-(v+vh)/k2))
: A. Fast component (Fast trace):

: Boltzmann:
        vh = -105.298 (mV)
        k = 12.359 (mV)
        vshift = 0.0 (mV)
        afast = 0.4471 : fraction that is fast.

: Tau
        taufac = 1.0 (1)
        taumin = 0 (ms)
        tausc1 = 0.00417518 (/ms)
        vtau1 = 87.0836 (mV)
        kfac1 = 28.1667 (mV)
        kfac2 = 21.4809 (mV)


: B. Slow component:
: (Run on date =  2014-01-01 12:52:22.777259 )
: Boltzmann:
        svh1 = -91.860 (mV)
        sk1 = 4.883 (mV) : double boltzmann
        svh2 = -110.209 (mV)
        sk2 = 3.927 (mV)
        svshift = 0.0 (mV)
        sba2 = 0.337216  : relative amplitude slow component 2 compared to slow 1 (slow2/(slow2+slow1))
        aslow = 0.5529 : total slow
		boltzmax = 0.5551729 : normalization factor 
							 : (computed numerically in Sage to make double boltz max = 1.0)

: stau
        staufac = 1.0 (1)
        staumin = 0 (ms)
        stausc1 = 0.00104354 (/ms)
        svtau1 = 105.816 (mV)
        skfac1 = 40.0291 (mV)
        skfac2 = 20.2273 (mV)

}

STATE {
		r
		s
}

ASSIGNED {
	gh (mho/cm2)
	i (mA/cm2)
	ih (mA/cm2)
	rinf
	rtau (ms)
	sinf
	stau (ms)
    q10 ()
}


BREAKPOINT {
	SOLVE states  METHOD cnexp
	gh = gbar*(afast*(r^2)+aslow*s) : Balance between fast and slow determined by afast and aslow
	ih = gh*(v - eh)
	i = ih
}


INITIAL {
	q10 = 3.0^((celsius - 22.0)/10.0 (degC)) : adjust for temperature...
	rates(v)
	r = rinf
	s = sinf
}

DERIVATIVE states {  : Updates state variables r and s
	rates(v)		  : at the current voltage
	r' = (rinf - r )/rtau
	s' = (sinf - s)/stau
}

LOCAL rt, st
PROCEDURE rates(v (mV)) {  : Computes rate and activation at voltage = v.

: fast component - standard HH-like kinetics.
	rinf = 1.0 / (1+exp((v - vh + vshift) / k))^0.5
	rt = tausc1*exp((v + vtau1 + vshift) / kfac1) + tausc1*exp(-(v + vtau1 + vshift) / kfac2)
	rtau = (taumin + taufac/rt)

: slow component
: double boltzman activation function (decreasing conductance), unequal sharing. 
	sinf = 1. / (1 + exp((v - svh1 + vshift) / sk1))
	st   = 1. / (1 + exp((v - svh2 + vshift) / sk2))
	sinf = (1-sba2)*sinf - sba2*st
	sinf = sinf/boltzmax : make sinf [0..1]
	
	stau = staufac / (stausc1*exp((v + svtau1 + vshift) / skfac1) + stausc1*exp(-(v + svtau1 + vshift) / skfac2))
	stau = (stau + staumin)
}

import pjsua

lib = pjsua.Lib()

for dev in lib.enum_snd_dev():
    print dev.name
    print "  input channels> %s" % dev.input_channels
    print " output channels> %s" % dev.input_channels
    print "      clock rate> %s" % dev.default_clock_rate
    print
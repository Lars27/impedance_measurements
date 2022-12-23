function ExamplePlotImpedance(src)
% function ExamplePlotImpedance(src)
%
% Example program, load and plot impedance measurement from HP8753, 
% saved as S11-parameters
% From functions written in LabVIEW at HBV-IMST

%--- Load raw data ---
trc= readtrace(src);

%--- Create frequency vector, calculate Z, and plot impedance  ---
f= [0:trc.Np-1]*trc.dx+trc.x0;      % Hz   Frequency vector

Zabs  = double( trc.y(:,1) ); 
Zphase= double( trc.y(:,2) ); 

Z = Zabs.*exp(1i*Zphase);

subplot(2,1,1)
semilogy(f, Zabs );
xlabel('Frequency [Hz]')
ylabel('Impedance magnitude [Ohm]')
grid on

subplot(2,1,2)
phi = angle(Z);
plot(f, Zphase);
xlabel('Frequency [Hz]')
ylabel('Phase [deg]')
ylim([-90 90])
set(gca, 'ytick', [-90:30:90])
grid on

return

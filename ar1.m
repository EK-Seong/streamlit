infl = readtable("infl.csv");
fe.ecpi0 = infl.realized_cpi-infl.cpi0;
fe.ecpi1 = infl.realized_cpi-infl.cpi1;
fe.ecpi2 = infl.realized_cpi-infl.cpi2;
fe.ecpi3 = infl.realized_cpi-infl.cpi3;
fe.ecpi4 = infl.realized_cpi-infl.cpi4;
fe = table2array(fe);

ehats = NaN(5,1);
for i = 1:size(fe,2)
    Z = [fe(:,i),lagmatrix(fe(:,i),1)];
    Z = rmmissing(Z);
    X = Z(:,2);
    Y = Z(:,1);
    ehats(i) = (X'*X\(X'*Y))*Y(end,1);
end
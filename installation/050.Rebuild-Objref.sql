--SQL to be executed during Module installation must be placed in the numbered *.sql files.
--Each file can include a single PL/SQL block
--PL/SQL block termination characters are not supported
--PL/SQL will be executed in the _pkg DB schema
--In case of error, module installation cannot proceed
--DBMS Output will be shown in UI
begin
    pkg_objref.rebuild_id_pkg_and_types();
    dbms_output.put_line('Object referencies were rebuilt');
end;

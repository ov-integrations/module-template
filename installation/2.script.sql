--SQL to be executed during Module installation must be placed in the numbered *.sql files.
--Each file can include a single PL/SQL block
--PL/SQL block termination characters are not supported
--PL/SQL will be executed in the _pkg DB schema
--In case of error, module installation cannot proceed
--Below is the sample code to add existing Trackor Type into the Tree:
declare
    c_rel_cardinality_one_many constant number := 2;
    v_jurisdiction_ttid xitor_type.xitor_type_id%type;
    v_rtid1 relation_type.relation_type_id%type;
begin
    select xitor_type_id 
      into v_jurisdiction_ttid
      from xitor_type
     where xitor_type = 'Jurisdiction';
     
    v_rtid1 := pkg_relation.new_relation_type(null, v_jurisdiction_ttid, c_rel_cardinality_one_many, 0, 0);
end;

/*
View for input into Eric Rippey's alliance selection
program for 2019 Deep Space
*/
create or replace view scouting.vw_er_export_2019orwil
as
select s.Team as team, s.`Match` as "match", upper(tm.alliance) as alliance,
	if(s.StartLvl = 2 and s.SandCross = 1, 1, 0) as shelf,
    s.ShipCargoTotal + s.RocketCargoTotal as balls,
    s.ShipHatchTotal + s.RocketHatchTotal as hatches,
    case s.ClimbSelf
		when 1 then 'P3'
        when 2 then 'P6'
        when 3 then 'P12'
        else 'NULL'
	end as climb,
    ifnull(AssistOther1,0) as climb_assist_a,
    ifnull(AssistOther2,0) as climb_assist_b,
    ifnull(WasAssisted,0) as climb_was_assisted
from data_2019orwil.scout s
join vw_team_match tm
	on tm.team_number = s.Team
    and tm.match_number = s.`Match`
where tm.tba_event_key = '2019orwil'
and tm.comp_level = 'qm'
;
{
  CLM 2.0: add "Energized" laser legendaries in new colours.

  For each colour, copies the existing Energized (Red Laser) set as new records:
    projectile  A1ALMPROJ_Variant_Type_Beam_Energized_Laser_<Colour>  -> model Effects\CLM\LaserRifleBeam<Colour>.nif
    legendary   A1ALMOMOD_Legendary_Weapon_Energized_Laser_<Colour>   "CLM: Energized (<Name> Laser)"
    recipes     co_A1ALMOMOD_Legendary_Weapon_Energized_Laser_<Colour>[FREE]
  Skips colours that already exist, so it is safe to re-run.
  Run with: python -m ack xedit run <this file> "Custom Legendary Modifications Remade.esp" --save
}
unit CLMAddEnergizedLaserColors;

const
  TargetFile = '{{TARGET}}';
  OutDir = '{{OUT}}';
  Prefix = 'Energized_Laser_';

var
  log: TStringList;
  f: IInterface;

function FindByEditorID(sig, edid: string): IInterface;
var
  g: IInterface;
begin
  Result := nil;
  g := GroupBySignature(f, sig);
  if Assigned(g) then
    Result := MainRecordByEditorID(g, edid);
end;

function LoadOrderID(e: IInterface): string;
begin
  Result := IntToHex(GetLoadOrderFormID(e), 8);
end;

procedure SetOverrideProjectile(omod, proj: IInterface);
var
  props, prop: IInterface;
  i: integer;
begin
  props := ElementByPath(omod, 'DATA\Properties');
  for i := 0 to ElementCount(props) - 1 do begin
    prop := ElementByIndex(props, i);
    if GetElementEditValues(prop, 'Property') = 'OverrideProjectile' then
      SetElementEditValues(prop, 'Value 1', LoadOrderID(proj));
  end;
end;

procedure AddColour(code, title: string; tProj, tOmod, tCost, tFree: IInterface);
var
  proj, omod, cost, free: IInterface;
begin
  if Assigned(FindByEditorID('OMOD', 'A1ALMOMOD_Legendary_Weapon_' + Prefix + code)) then begin
    log.Add('skip ' + code + ' (already present)');
    Exit;
  end;

  proj := wbCopyElementToFile(tProj, f, True, True);
  SetEditorID(proj, 'A1ALMPROJ_Variant_Type_Beam_' + Prefix + code);
  SetElementEditValues(proj, 'Model\MODL', 'Effects\CLM\LaserRifleBeam' + code + '.nif');
  if Assigned(ElementByPath(proj, 'Model\MODT')) then
    RemoveElement(ElementByPath(proj, 'Model'), 'MODT');

  omod := wbCopyElementToFile(tOmod, f, True, True);
  SetEditorID(omod, 'A1ALMOMOD_Legendary_Weapon_' + Prefix + code);
  SetElementEditValues(omod, 'FULL', 'CLM: Energized (' + title + ' Laser)');
  SetOverrideProjectile(omod, proj);

  cost := wbCopyElementToFile(tCost, f, True, True);
  SetEditorID(cost, 'co_A1ALMOMOD_Legendary_Weapon_' + Prefix + code);
  SetElementEditValues(cost, 'CNAM', LoadOrderID(omod));

  free := wbCopyElementToFile(tFree, f, True, True);
  SetEditorID(free, 'co_A1ALMOMOD_Legendary_Weapon_' + Prefix + code + 'FREE');
  SetElementEditValues(free, 'CNAM', LoadOrderID(omod));

  log.Add(Format('added %s: PROJ %s, OMOD %s "%s", COBJ %s + %s',
    [code, LoadOrderID(proj), LoadOrderID(omod), GetElementEditValues(omod, 'FULL'), LoadOrderID(cost), LoadOrderID(free)]));
end;

function Initialize: integer;
var
  i: integer;
  tProj, tOmod, tCost, tFree: IInterface;
begin
  log := TStringList.Create;
  for i := 0 to FileCount - 1 do
    if GetFileName(FileByIndex(i)) = TargetFile then
      f := FileByIndex(i);

  if not Assigned(f) then
    log.Add('ERROR: target plugin not loaded')
  else begin
    tProj := FindByEditorID('PROJ', 'A1ALMPROJ_Variant_Type_Beam_' + Prefix + 'Red');
    tOmod := FindByEditorID('OMOD', 'A1ALMOMOD_Legendary_Weapon_' + Prefix + 'Red');
    tCost := FindByEditorID('COBJ', 'co_A1ALMOMOD_Legendary_Weapon_' + Prefix + 'Red');
    tFree := FindByEditorID('COBJ', 'co_A1ALMOMOD_Legendary_Weapon_' + Prefix + 'RedFREE');
    if not (Assigned(tProj) and Assigned(tOmod) and Assigned(tCost) and Assigned(tFree)) then
      log.Add('ERROR: Energized (Red Laser) template records not found')
    else begin
      AddColour('Green', 'Green', tProj, tOmod, tCost, tFree);
      AddColour('Purple', 'Purple', tProj, tOmod, tCost, tFree);
      AddColour('Gold', 'Gold', tProj, tOmod, tCost, tFree);
      AddColour('Orange', 'Orange', tProj, tOmod, tCost, tFree);
      AddColour('Pink', 'Pink', tProj, tOmod, tCost, tFree);
      AddColour('DeepBlue', 'Deep Blue', tProj, tOmod, tCost, tFree);
    end;
  end;

  log.SaveToFile(OutDir + 'result.txt');
  log.Clear;
  log.Add('ok');
  log.SaveToFile(OutDir + 'DONE.txt');
  log.Free;
  Result := 0;
end;

end.

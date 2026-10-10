{
  CLM 2.0: give each coloured Energized laser its own impact effects.

  Impact sparks and the glowing spots left on surfaces come from the gun's impact data set, not the projectile.
  On a laser gun that set is red, so the coloured lasers still hit with red impacts. Following the vanilla
  light-blue laser, each colour gets:
    A1ALMIPCT_LaserSmall_<Colour>  copy of LaserLtBlueSmallImpact: model ImpactLaser<Colour>Small.nif, decal colour
    A1ALMIPCT_LaserShell_<Colour>  copy of LaserArmoredBlueImpact: model ImpactLaser<Colour>VsShell.nif
    A1ALMIPDS_Laser_<Colour>       copy of LaserLtBlueSmallImpactSet pointing at the two impacts above
  and the legendary sets ImpactDataSet to it (the same OMOD property Salvaged Assaultron's Beaming uses).
  Models and decal colours come from tools/assets/laser_colors.py. Safe to re-run.
}
unit CLMEnergizedLaserImpacts;

const
  TargetFile = '{{TARGET}}';
  OutDir = '{{OUT}}';

var
  log: TStringList;
  f, fo4: IInterface;

function FindChild(e: IInterface; nm: string): IInterface;
var
  i: integer;
  c: IInterface;
begin
  Result := nil;
  for i := 0 to ElementCount(e) - 1 do begin
    c := ElementByIndex(e, i);
    if (Name(c) = nm) or (Pos(nm + ' - ', Name(c)) = 1) or (Pos(' - ' + nm, Name(c)) > 0) then begin
      Result := c;
      Exit;
    end;
    Result := FindChild(c, nm);
    if Assigned(Result) then
      Exit;
  end;
end;

function Rec(fl: IInterface; sig, edid: string): IInterface;
var
  g: IInterface;
begin
  Result := nil;
  g := GroupBySignature(fl, sig);
  if Assigned(g) then
    Result := MainRecordByEditorID(g, edid);
end;

function LoID(e: IInterface): string;
begin
  Result := IntToHex(GetLoadOrderFormID(e), 8);
end;

function CopyOnce(src: IInterface; sig, edid: string): IInterface;
begin
  Result := Rec(f, sig, edid);
  if not Assigned(Result) then begin
    Result := wbCopyElementToFile(src, f, True, True);
    SetEditorID(Result, edid);
  end;
end;

procedure SetModel(e: IInterface; path: string);
begin
  SetElementEditValues(e, 'Model\MODL', path);
  if Assigned(ElementByPath(e, 'Model\MODT')) then
    RemoveElement(ElementByPath(e, 'Model'), 'MODT');
end;

function PropertyOf(omod: IInterface; pname: string): IInterface;
var
  props, p: IInterface;
  i: integer;
begin
  Result := nil;
  props := ElementByPath(omod, 'DATA\Properties');
  for i := 0 to ElementCount(props) - 1 do begin
    p := ElementByIndex(props, i);
    if GetElementEditValues(p, 'Property') = pname then begin
      Result := p;
      Exit;
    end;
  end;
end;

procedure Apply(code: string; r, g, b: integer; tSmall, tShell, tSet, tProp: IInterface);
var
  small, shell, iset, omod, color, entries, entry, prop: IInterface;
  i: integer;
  imp: string;
begin
  omod := Rec(f, 'OMOD', 'A1ALMOMOD_Legendary_Weapon_Energized_Laser_' + code);
  if not Assigned(omod) then begin
    log.Add('ERROR: legendary for ' + code + ' not found');
    Exit;
  end;

  small := CopyOnce(tSmall, 'IPCT', 'A1ALMIPCT_LaserSmall_' + code);
  SetModel(small, 'Effects\CLM\ImpactLaser' + code + 'Small.nif');
  color := FindChild(small, 'Color');
  SetElementEditValues(color, 'Red', IntToStr(r));
  SetElementEditValues(color, 'Green', IntToStr(g));
  SetElementEditValues(color, 'Blue', IntToStr(b));

  shell := CopyOnce(tShell, 'IPCT', 'A1ALMIPCT_LaserShell_' + code);
  SetModel(shell, 'Effects\CLM\ImpactLaser' + code + 'VsShell.nif');

  iset := CopyOnce(tSet, 'IPDS', 'A1ALMIPDS_Laser_' + code);
  entries := ElementByName(iset, 'Data');  // IPDS: array of PNAM {Material, Impact}
  for i := 0 to ElementCount(entries) - 1 do begin
    entry := ElementByIndex(entries, i);
    imp := GetElementEditValues(entry, 'Impact');
    if Pos('LaserLtBlueSmallImpact', imp) > 0 then
      SetElementEditValues(entry, 'Impact', LoID(small))
    else if Pos('LaserArmoredBlueImpact', imp) > 0 then
      SetElementEditValues(entry, 'Impact', LoID(shell));
  end;

  prop := PropertyOf(omod, 'ImpactDataSet');
  if not Assigned(prop) then
    prop := ElementAssign(ElementByPath(omod, 'DATA\Properties'), HighInteger, tProp, False);
  SetElementEditValues(prop, 'Value 1', LoID(iset));

  log.Add(Format('%s: IPCT %s + %s, IPDS %s, OMOD property %s %s %s', [code, LoID(small), LoID(shell), LoID(iset),
    GetElementEditValues(prop, 'Property'), GetElementEditValues(prop, 'Function Type'), GetElementEditValues(prop, 'Value 1')]));
  for i := 0 to ElementCount(entries) - 1 do
    log.Add('    ' + GetElementEditValues(ElementByIndex(entries, i), 'Material') + ' -> ' +
      GetElementEditValues(ElementByIndex(entries, i), 'Impact'));
end;

function Initialize: integer;
var
  i: integer;
  tSmall, tShell, tSet, tProp: IInterface;
begin
  log := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    if GetFileName(FileByIndex(i)) = TargetFile then
      f := FileByIndex(i);
    if GetFileName(FileByIndex(i)) = 'Fallout4.esm' then
      fo4 := FileByIndex(i);
  end;
  tSmall := Rec(fo4, 'IPCT', 'LaserLtBlueSmallImpact');
  tShell := Rec(fo4, 'IPCT', 'LaserArmoredBlueImpact');
  tSet := Rec(fo4, 'IPDS', 'LaserLtBlueSmallImpactSet');
  tProp := PropertyOf(Rec(f, 'OMOD', 'A1ALMOMOD_Legendary_Weapon_Assaultrons'), 'ImpactDataSet');
  if not Assigned(tProp) then
    log.Add('ERROR: template ImpactDataSet property (Salvaged Assaultron''s Beaming) not found')
  else if not (Assigned(f) and Assigned(tSmall) and Assigned(tShell) and Assigned(tSet)) then
    log.Add('ERROR: target plugin or vanilla light-blue impact records not found')
  else begin
    Apply('Green', 70, 236, 70, tSmall, tShell, tSet, tProp);
    Apply('Purple', 167, 70, 236, tSmall, tShell, tSet, tProp);
    Apply('Gold', 236, 203, 70, tSmall, tShell, tSet, tProp);
    Apply('Orange', 236, 136, 70, tSmall, tShell, tSet, tProp);
    Apply('Pink', 236, 70, 181, tSmall, tShell, tSet, tProp);
    Apply('DeepBlue', 70, 112, 236, tSmall, tShell, tSet, tProp);
  end;
  log.SaveToFile(OutDir + 'result.txt');
  log.Clear;
  log.Add('ok');
  log.SaveToFile(OutDir + 'DONE.txt');
  log.Free;
  Result := 0;
end;

end.

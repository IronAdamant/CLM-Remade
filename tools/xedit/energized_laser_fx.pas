{
  CLM 2.0: give each coloured Energized laser its own muzzle flash and light.

  The first version copied Energized (Red Laser), so the new colours still used the red muzzle flash
  (Effects\MuzLaserRifle01.nif) and the red light (WeapLightLaserBeam). Following how the vanilla light-blue
  laser does it, each colour now gets:
    light       A1ALMLIGH_Laser_<Colour>  - copy of WeapLightLaserBeamLtBlue with the colour's RGB
    projectile  muzzle flash model Effects\CLM\MuzLaserRifle<Colour>.nif, Light + Muzzle Flash Light = that light
  Light colours come from tools/assets/laser_colors.py. Safe to re-run.
}
unit CLMEnergizedLaserFX;

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

procedure SetField(e: IInterface; nm, value: string);
var
  c: IInterface;
begin
  c := FindChild(e, nm);
  if Assigned(c) then
    SetEditValue(c, value)
  else
    log.Add('  WARNING: field "' + nm + '" not found on ' + EditorID(e));
end;

procedure Apply(code: string; r, g, b: integer; template: IInterface);
var
  light, proj, color: IInterface;
  lid: string;
begin
  proj := Rec(f, 'PROJ', 'A1ALMPROJ_Variant_Type_Beam_Energized_Laser_' + code);
  if not Assigned(proj) then begin
    log.Add('ERROR: projectile for ' + code + ' not found');
    Exit;
  end;

  light := Rec(f, 'LIGH', 'A1ALMLIGH_Laser_' + code);
  if not Assigned(light) then begin
    light := wbCopyElementToFile(template, f, True, True);
    SetEditorID(light, 'A1ALMLIGH_Laser_' + code);
  end;
  color := FindChild(light, 'Color');
  SetElementEditValues(color, 'Red', IntToStr(r));
  SetElementEditValues(color, 'Green', IntToStr(g));
  SetElementEditValues(color, 'Blue', IntToStr(b));

  lid := IntToHex(GetLoadOrderFormID(light), 8);
  SetElementEditValues(proj, 'Muzzle Flash Model\NAM1', 'Effects\CLM\MuzLaserRifle' + code + '.nif');
  SetField(proj, 'Light', lid);
  SetField(proj, 'Muzzle Flash - Light', lid);

  log.Add(Format('%s: LIGH %s RGB(%s,%s,%s) | PROJ muzzle=%s light=%s muzzle light=%s', [code, lid,
    GetElementEditValues(color, 'Red'), GetElementEditValues(color, 'Green'), GetElementEditValues(color, 'Blue'),
    GetElementEditValues(proj, 'Muzzle Flash Model\NAM1'),
    GetEditValue(FindChild(proj, 'Light')), GetEditValue(FindChild(proj, 'Muzzle Flash - Light'))]));
end;

function Initialize: integer;
var
  i: integer;
  template: IInterface;
begin
  log := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    if GetFileName(FileByIndex(i)) = TargetFile then
      f := FileByIndex(i);
    if GetFileName(FileByIndex(i)) = 'Fallout4.esm' then
      fo4 := FileByIndex(i);
  end;
  template := Rec(fo4, 'LIGH', 'WeapLightLaserBeamLtBlue');
  if not (Assigned(f) and Assigned(template)) then
    log.Add('ERROR: target plugin or WeapLightLaserBeamLtBlue not found')
  else begin
    Apply('Green', 17, 255, 17, template);
    Apply('Purple', 156, 17, 255, template);
    Apply('Gold', 255, 207, 17, template);
    Apply('Orange', 255, 112, 17, template);
    Apply('Pink', 255, 17, 176, template);
    Apply('DeepBlue', 17, 77, 255, template);
  end;
  log.SaveToFile(OutDir + 'result.txt');
  log.Clear;
  log.Add('ok');
  log.SaveToFile(OutDir + 'DONE.txt');
  log.Free;
  Result := 0;
end;

end.

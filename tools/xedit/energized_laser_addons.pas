{
  CLM 2.0: register the coloured laser add-on nodes.

  Laser effect models attach shared particle effects (muzzle sparks, impact sparks, impact smoke, impact wave)
  by a global add-on index, defined by ADDN records. tools/assets/laser_colors.py points each colour's models at
  indexes 1500 + colour*10 + kind (a free block above all official content, which stays below 1000); this script creates the
  matching ADDN records as copies of the vanilla light-blue ones. The colour/kind numbering here must match
  COLORS and ADDON_KINDS in laser_colors.py. Safe to re-run.
}
unit CLMEnergizedLaserAddons;

const
  TargetFile = '{{TARGET}}';
  OutDir = '{{OUT}}';
  AddonBase = 1500;

var
  log: TStringList;
  f, fo4: IInterface;

function Rec(fl: IInterface; sig, edid: string): IInterface;
var
  g: IInterface;
begin
  Result := nil;
  g := GroupBySignature(fl, sig);
  if Assigned(g) then
    Result := MainRecordByEditorID(g, edid);
end;

function KindName(k: integer): string;
begin
  case k of
    1: Result := 'MuzSparks';
    2: Result := 'ImpactSparks';
    3: Result := 'ImpactSmoke';
    4: Result := 'ImpactWave';
  end;
end;

function KindTemplate(k: integer): string;
begin
  case k of
    1: Result := 'MPSMuzSparksLaser02LtBlue';
    2: Result := 'MPSLaserImpactSparksLtBlue';
    3: Result := 'MPSSmokeLaserImpactLtBlue';
    4: Result := 'MPSLaserWaveImpactLtBlue';
  end;
end;

function ColourName(c: integer): string;
begin
  case c of
    1: Result := 'Green';
    2: Result := 'Purple';
    3: Result := 'Gold';
    4: Result := 'Orange';
    5: Result := 'Pink';
    6: Result := 'DeepBlue';
  end;
end;

function Initialize: integer;
var
  i, c, k, idx: integer;
  tmpl, addn: IInterface;
  edid: string;
begin
  log := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    if GetFileName(FileByIndex(i)) = TargetFile then
      f := FileByIndex(i);
    if GetFileName(FileByIndex(i)) = 'Fallout4.esm' then
      fo4 := FileByIndex(i);
  end;
  if not Assigned(f) then
    log.Add('ERROR: target plugin not loaded')
  else
    for c := 1 to 6 do
      for k := 1 to 4 do begin
        idx := AddonBase + c * 10 + k;
        edid := 'A1ALMADDN_Laser' + KindName(k) + '_' + ColourName(c);
        addn := Rec(f, 'ADDN', edid);
        if not Assigned(addn) then begin
          tmpl := Rec(fo4, 'ADDN', KindTemplate(k));
          if not Assigned(tmpl) then begin
            log.Add('ERROR: template ' + KindTemplate(k) + ' not found');
            Continue;
          end;
          addn := wbCopyElementToFile(tmpl, f, True, True);
          SetEditorID(addn, edid);
        end;
        SetElementEditValues(addn, 'Model\MODL', 'Effects\CLM\MPS' + KindName(k) + ColourName(c) + '.nif');
        if Assigned(ElementByPath(addn, 'Model\MODT')) then
          RemoveElement(ElementByPath(addn, 'Model'), 'MODT');
        SetElementEditValues(addn, 'DATA', IntToStr(idx));
        log.Add(Format('%s: index %s model %s', [edid, GetElementEditValues(addn, 'DATA'), GetElementEditValues(addn, 'Model\MODL')]));
      end;
  log.SaveToFile(OutDir + 'result.txt');
  log.Clear;
  log.Add('ok');
  log.SaveToFile(OutDir + 'DONE.txt');
  log.Free;
  Result := 0;
end;

end.

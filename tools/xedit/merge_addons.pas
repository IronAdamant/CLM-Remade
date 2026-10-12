{
  CLM 2.0: merge the DLC add-ons back into the main plugin (the reverse of move_to_addon.pas).

  Parameters: RECORDS (text file, one line per record to merge: "editor ID<TAB>object ID in hex", the object ID
  empty to let xEdit pick one), MASTERS (comma-separated DLC masters to add).
  Steps: add the DLC masters to the main plugin; make a placeholder record there for each listed record, with its
  object ID from the list (the ID it had in the main plugin before it moved, so 1.09 saves keep it); point the
  references between listed records at the placeholders; verify that none still references an add-on record; then
  copy each record into the main plugin and give the copy its placeholder's form ID. xEdit can only copy a record
  into the main plugin once it references nothing in an add-on, so the add-ons are changed in memory: the caller
  (tools/addons/merge_into_main.py) puts the saved copies back.
}
unit CLMMergeAddons;

const
  TargetFile = '{{TARGET}}';
  OutDir = '{{OUT}}';
  RecordsFile = '{{RECORDS}}';
  Masters = '{{MASTERS}}';

var
  log: TStringList;

function FindIn(fl: IInterface; edid: string): IInterface;
var
  i: integer;
  g: IInterface;
begin
  Result := nil;
  for i := 0 to ElementCount(fl) - 1 do begin
    g := ElementByIndex(fl, i);
    if Signature(g) = 'GRUP' then begin
      Result := MainRecordByEditorID(g, edid);
      if Assigned(Result) then
        Exit;
    end;
  end;
end;

function Initialize: integer;
var
  i, j, k, nErr, tab: integer;
  f, fl, rec, cp, g, ph: IInterface;
  lines, olds, news, addons, ms, done: TStringList;
  line, edid, hex: string;
  fid: cardinal;
begin
  log := TStringList.Create;
  lines := TStringList.Create;
  olds := TStringList.Create;
  news := TStringList.Create;
  addons := TStringList.Create;
  ms := TStringList.Create;
  nErr := 0;
  for i := 0 to FileCount - 1 do begin
    fl := FileByIndex(i);
    if GetFileName(fl) = TargetFile then
      f := fl
    else if Pos('CLM - ', GetFileName(fl)) = 1 then
      addons.AddObject(GetFileName(fl), fl);
  end;
  log.Add('add-ons loaded: ' + addons.CommaText);

  // 1. find every record first; abort before changing anything if one is missing
  lines.LoadFromFile(RecordsFile);
  for i := 0 to lines.Count - 1 do begin
    line := lines[i];
    if Trim(line) = '' then
      Continue;
    tab := Pos(#9, line);
    edid := Copy(line, 1, tab - 1);
    rec := nil;
    for j := 0 to addons.Count - 1 do
      if not Assigned(rec) then
        rec := FindIn(ObjectToElement(addons.Objects[j]), edid);
    if not Assigned(rec) then begin
      log.Add('ERROR  not found in any add-on: ' + edid);
      Inc(nErr);
    end
    else
      olds.AddObject(Copy(line, tab + 1, 8), rec);
  end;

  if nErr = 0 then begin
    // 2. masters
    ms.CommaText := Masters;
    for i := 0 to ms.Count - 1 do
      AddMasterIfMissing(f, ms[i]);
    SortMasters(f);

    // 3. a placeholder in the main plugin per record, holding its final form ID (its old one where known)
    for i := 0 to olds.Count - 1 do begin
      rec := ObjectToElement(olds.Objects[i]);
      g := GroupBySignature(f, Signature(rec));
      if not Assigned(g) then
        g := Add(f, Signature(rec), True);
      ph := Add(g, Signature(rec), True);
      hex := olds[i];
      if hex <> '' then
        SetLoadOrderFormID(ph, (GetLoadOrderFormID(ph) and $FF000000) or StrToInt('$' + hex));
      news.AddObject(EditorID(rec), ph);
    end;

    // 4. in the add-ons (in memory only), point every reference between merged records at the placeholders; a
    // copy can only be made once the record references nothing in an add-on
    for i := 0 to olds.Count - 1 do
      for j := 0 to olds.Count - 1 do
        CompareExchangeFormID(ObjectToElement(olds.Objects[i]),
          GetLoadOrderFormID(ObjectToElement(olds.Objects[j])),
          GetLoadOrderFormID(ObjectToElement(news.Objects[j])));

    // 5. verify: no merged record may still reference any add-on record (merged or not)
    for i := 0 to olds.Count - 1 do
      for k := 0 to addons.Count - 1 do begin
        fl := ObjectToElement(addons.Objects[k]);
        for j := 0 to RecordCount(fl) - 1 do begin
          rec := RecordByIndex(fl, j);
          if Signature(rec) = 'TES4' then
            Continue;
          if CompareExchangeFormID(ObjectToElement(olds.Objects[i]), GetLoadOrderFormID(rec),
               GetLoadOrderFormID(rec)) then begin
            log.Add('ERROR  ' + news[i] + ' still references ' + addons[k] + ' ' + EditorID(rec));
            Inc(nErr);
          end;
        end;
      end;

    // 6. copy each record into the main plugin and move it onto its placeholder's form ID
    if nErr = 0 then begin
      for i := 0 to olds.Count - 1 do begin
        ph := ObjectToElement(news.Objects[i]);
        fid := GetLoadOrderFormID(ph);
        cp := wbCopyElementToFile(ObjectToElement(olds.Objects[i]), f, True, True);
        Remove(ph);
        SetLoadOrderFormID(cp, fid);
      end;
      log.Add(Format('copied %d records', [olds.Count]));
    end;
    log.Add('masters: ' + IntToStr(MasterCount(f)));
    for i := 0 to MasterCount(f) - 1 do
      log.Add('  ' + GetFileName(MasterByIndex(f, i)));
  end;

  log.Insert(0, Format('%d errors', [nErr]));
  log.SaveToFile(OutDir + 'result.txt');
  done := TStringList.Create;
  done.Add('ok');
  done.SaveToFile(OutDir + 'DONE.txt');
  done.Free;
  lines.Free;
  olds.Free;
  news.Free;
  addons.Free;
  ms.Free;
  log.Free;
  Result := 0;
end;

end.

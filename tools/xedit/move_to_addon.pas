{
  CLM 2.0: move records from the main plugin into a new ESL-flagged add-on plugin.

  Parameters: ADDON (new plugin file name), DLC (the DLC master it needs), RECORDS (text file of editor IDs).
  Steps: create the add-on (ESL flag), add masters (Fallout4.esm, the DLC, the main plugin), copy every listed record
  into it as a new record, re-point references between the copies (a moved legendary must use the moved projectile,
  not the original), verify that no copy still references a listed original, and only then delete the originals
  from the main plugin. If anything fails, nothing is deleted.
}
unit CLMMoveToAddon;

const
  TargetFile = '{{TARGET}}';
  OutDir = '{{OUT}}';
  AddonFile = '{{ADDON}}';
  DlcMaster = '{{DLC}}';
  RecordsFile = '{{RECORDS}}';

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
  i, j, nErr: integer;
  f, nf, rec, cp: IInterface;
  names, olds, news, done: TStringList;
  line: string;
begin
  log := TStringList.Create;
  names := TStringList.Create;
  olds := TStringList.Create;
  news := TStringList.Create;
  nErr := 0;
  for i := 0 to FileCount - 1 do
    if GetFileName(FileByIndex(i)) = TargetFile then
      f := FileByIndex(i);

  names.LoadFromFile(RecordsFile);
  // 1. find every original first; abort before creating anything if one is missing
  for i := 0 to names.Count - 1 do begin
    line := Trim(names[i]);
    if (line = '') or (Copy(line, 1, 1) = '#') then
      Continue;
    rec := FindIn(f, line);
    if not Assigned(rec) then begin
      log.Add('ERROR  not found in main plugin: ' + line);
      Inc(nErr);
    end
    else
      olds.AddObject(line, rec);
  end;

  if nErr = 0 then begin
    // 2. new ESL-flagged plugin with its masters
    // Reuse the add-on if it is already loaded (run with --also-load), otherwise create it.
    nf := nil;
    for i := 0 to FileCount - 1 do
      if GetFileName(FileByIndex(i)) = AddonFile then
        nf := FileByIndex(i);
    if Assigned(nf) then
      log.Add('appending to existing ' + GetFileName(nf))
    else begin
      nf := AddNewFileName(AddonFile, True);
      // New files start their object counter at 1, but IDs below 0x800 are reserved and an ESL must use
      // 0x800-0xFFF: start at 0x800 before any record is added.
      SetElementNativeValues(ElementByIndex(nf, 0), 'HEDR\Next Object ID', $800);
      log.Add('created ' + GetFileName(nf));
    end;
    AddMasterIfMissing(nf, 'Fallout4.esm');
    AddMasterIfMissing(nf, DlcMaster);
    AddMasterIfMissing(nf, TargetFile);

    // 3. copy
    for i := 0 to olds.Count - 1 do begin
      cp := wbCopyElementToFile(ObjectToElement(olds.Objects[i]), nf, True, True);
      news.AddObject(olds[i], cp);
    end;
    log.Add(Format('copied %d records', [news.Count]));

    // 4. re-point references between copies
    for i := 0 to news.Count - 1 do
      for j := 0 to olds.Count - 1 do
        CompareExchangeFormID(ObjectToElement(news.Objects[i]),
          GetLoadOrderFormID(ObjectToElement(olds.Objects[j])),
          GetLoadOrderFormID(ObjectToElement(news.Objects[j])));

    // 5. verify: no copy may still reference a listed original
    for i := 0 to news.Count - 1 do
      for j := 0 to olds.Count - 1 do
        if CompareExchangeFormID(ObjectToElement(news.Objects[i]),
             GetLoadOrderFormID(ObjectToElement(olds.Objects[j])),
             GetLoadOrderFormID(ObjectToElement(olds.Objects[j]))) then begin
          log.Add('ERROR  ' + olds[i] + ' copy still references original ' + olds[j]);
          Inc(nErr);
        end;

    // 6. delete originals only if everything checked out
    if nErr = 0 then begin
      for i := 0 to olds.Count - 1 do
        Remove(ObjectToElement(olds.Objects[i]));
      log.Add(Format('deleted %d originals from %s', [olds.Count, TargetFile]));
    end
    else
      log.Add('NOT deleting originals because of errors above');
  end;

  log.Insert(0, Format('%d errors', [nErr]));
  log.SaveToFile(OutDir + 'result.txt');
  done := TStringList.Create;
  done.Add('ok');
  done.SaveToFile(OutDir + 'DONE.txt');
  done.Free;
  names.Free;
  olds.Free;
  news.Free;
  log.Free;
  Result := 0;
end;

end.

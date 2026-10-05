"use client";

import { Camera, ImagePlus, Save, Trash2, UserRound } from "lucide-react";
import { ChangeEvent, useEffect, useRef, useState } from "react";

type Profile = { first_name: string; last_name: string; email: string; role: string; avatar_data: string | null };

async function photoData(file: File): Promise<string> {
  if (!file.type.startsWith("image/")) throw new Error("Choose an image file.");
  if (file.size > 8_000_000) throw new Error("Choose an image smaller than 8 MB.");
  const image = new Image();
  const url = URL.createObjectURL(file);
  try {
    image.src = url;
    await image.decode();
    const scale = Math.min(1, 512 / Math.max(image.width, image.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(image.width * scale));
    canvas.height = Math.max(1, Math.round(image.height * scale));
    canvas.getContext("2d")?.drawImage(image, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.82);
  } finally { URL.revokeObjectURL(url); }
}

export function ProfileEditor() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  async function loadProfile() {
    const response = await fetch("/api/backend/auth/me", { cache: "no-store" });
    if (!response.ok) throw new Error("Could not load your profile.");
    const data = await response.json() as Profile;
    setProfile(data);
    setFirstName(data.first_name);
    setLastName(data.last_name);
  }

  useEffect(() => { loadProfile().catch((reason: Error) => setError(reason.message)); }, []);

  async function save(changes: Partial<Profile>) {
    setBusy(true); setError(""); setMessage("");
    try {
      const response = await fetch("/api/backend/auth/me", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(changes) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Could not save your profile.");
      setProfile(result); setFirstName(result.first_name); setLastName(result.last_name);
      setMessage("Profile saved successfully.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save your profile."); }
    finally { setBusy(false); }
  }

  async function handlePhoto(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true); setError(""); setMessage("");
    try { await save({ avatar_data: await photoData(file) }); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not read that image."); }
    finally { setBusy(false); event.target.value = ""; }
  }

  if (!profile) return <section className="profile-card"><p>{error || "Loading your profile…"}</p></section>;
  const fullName = `${profile.first_name} ${profile.last_name}`;
  const initials = fullName.split(" ").filter(Boolean).map((part) => part[0]).join("").slice(0, 2).toUpperCase();

  return <div className="profile-page">
    <header className="profile-heading"><div><span className="feature-kicker">YOUR ACCOUNT</span><h1>Profile settings</h1><p>Update your personal details and profile photo.</p></div></header>
    {(message || error) && <p className={error ? "feature-message feature-error" : "feature-message feature-success"} role="status">{message || error}</p>}
    <section className="profile-card profile-photo-card"><div className="profile-photo">{profile.avatar_data ? <img src={profile.avatar_data} alt={`${fullName} profile`} /> : <span>{initials || <UserRound size={32}/>}</span>}</div><div className="profile-photo-copy"><h2>Profile photo</h2><p>Use a square photo. We resize it to a small JPEG before saving.</p><div className="profile-photo-actions"><input ref={fileInput} type="file" accept="image/png,image/jpeg,image/webp" onChange={handlePhoto} hidden/><button className="button" type="button" disabled={busy} onClick={() => fileInput.current?.click()}>{profile.avatar_data ? <Camera size={15}/> : <ImagePlus size={15}/>} {profile.avatar_data ? "Change photo" : "Add photo"}</button>{profile.avatar_data && <button className="button button-outline" type="button" disabled={busy} onClick={() => save({ avatar_data: null })}><Trash2 size={15}/> Remove photo</button>}</div></div></section>
    <form className="profile-card profile-form" onSubmit={(event) => { event.preventDefault(); save({ first_name: firstName, last_name: lastName }); }}>
      <div className="profile-section-title"><span className="profile-section-icon"><UserRound size={17}/></span><span><h2>Personal information</h2><p>Edit the name shown across your workspace.</p></span></div>
      <div className="profile-fields"><label>First name<input value={firstName} onChange={(event) => setFirstName(event.target.value)} required maxLength={100}/></label><label>Last name<input value={lastName} onChange={(event) => setLastName(event.target.value)} required maxLength={100}/></label><label className="profile-wide">Email address<input value={profile.email} readOnly/><small>Email address is used to sign in and cannot be changed here.</small></label><label className="profile-wide">Workspace role<input value={profile.role.replaceAll("_", " ")} readOnly/></label></div>
      <footer className="profile-form-footer"><span>Your photo and name are saved to your account.</span><button className="button" disabled={busy}><Save size={15}/>{busy ? "Saving…" : "Save changes"}</button></footer>
    </form>
  </div>;
}

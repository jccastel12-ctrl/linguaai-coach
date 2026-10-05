"use client";

export type TutorAvatarState = "idle" | "listening" | "thinking" | "speaking";
export type TutorAvatarProfileId = "lia" | "alex" | "mila";

export interface TutorAvatarProfile {
  id: TutorAvatarProfileId;
  name: string;
  description: string;
  className: string;
  voiceRate: number;
  voicePitch: number;
}

export const tutorAvatarProfiles: TutorAvatarProfile[] = [
  {
    id: "lia",
    name: "Lia",
    description: "Cálida y clara",
    className: "avatar-theme-lia",
    voiceRate: 0.94,
    voicePitch: 1.06,
  },
  {
    id: "alex",
    name: "Alex",
    description: "Sereno y directo",
    className: "avatar-theme-alex",
    voiceRate: 0.97,
    voicePitch: 0.95,
  },
  {
    id: "mila",
    name: "Mila",
    description: "Dinámica y cercana",
    className: "avatar-theme-mila",
    voiceRate: 1.02,
    voicePitch: 1,
  },
];

export function getTutorAvatarProfile(id: string): TutorAvatarProfile {
  return tutorAvatarProfiles.find((profile) => profile.id === id) ?? tutorAvatarProfiles[0];
}

const stateLabels: Record<TutorAvatarState, string> = {
  idle: "Lista para practicar",
  listening: "Te escucho",
  thinking: "Pensando",
  speaking: "Hablando",
};

interface TutorAvatarProps {
  profile: TutorAvatarProfile;
  state?: TutorAvatarState;
  compact?: boolean;
  showLabel?: boolean;
}

export function TutorAvatar({
  profile,
  state = "idle",
  compact = false,
  showLabel = true,
}: TutorAvatarProps) {
  return (
    <div
      className={`tutor-avatar ${profile.className} tutor-avatar-${state}${compact ? " tutor-avatar-compact" : ""}`}
      aria-label={`${profile.name}, tutor virtual. ${stateLabels[state]}.`}
      role="img"
    >
      <div className="avatar-stage" aria-hidden="true">
        <span className="avatar-orbit avatar-orbit-one" />
        <span className="avatar-orbit avatar-orbit-two" />
        <div className="avatar-bust">
          <div className="avatar-neck" />
          <div className="avatar-shoulders" />
          <div className="avatar-head">
            <div className="avatar-hair avatar-hair-back" />
            <div className="avatar-ear avatar-ear-left" />
            <div className="avatar-ear avatar-ear-right" />
            <div className="avatar-face">
              <div className="avatar-hair avatar-hair-front" />
              <div className="avatar-brow avatar-brow-left" />
              <div className="avatar-brow avatar-brow-right" />
              <div className="avatar-eye avatar-eye-left"><span /></div>
              <div className="avatar-eye avatar-eye-right"><span /></div>
              <div className="avatar-nose" />
              <div className="avatar-mouth"><span /></div>
            </div>
          </div>
        </div>
        <div className="avatar-sound-bars" aria-hidden="true">
          <span /><span /><span /><span /><span />
        </div>
        <div className="avatar-thinking-dots" aria-hidden="true"><span /><span /><span /></div>
      </div>
      {showLabel ? (
        <div className="avatar-caption">
          <strong>{profile.name}</strong>
          <span>{stateLabels[state]}</span>
        </div>
      ) : null}
    </div>
  );
}

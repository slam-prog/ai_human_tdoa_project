<svg xmlns="http://www.w3.org/2000/svg"
     width="1400"
     height="620"
     viewBox="0 0 1400 620">

  <style>
    .title {
      font: bold 26px Arial;
      fill: #1f2937;
    }

    .label {
      font: 18px Arial;
      fill: #111827;
    }

    .small {
      font: 15px Arial;
      fill: #374151;
    }

    .axis {
      stroke: #111827;
      stroke-width: 2;
    }

    .gate {
      fill: #fde68a;
      stroke: #92400e;
      stroke-width: 2;
    }

    .audio {
      fill: #bbf7d0;
      stroke: #166534;
      stroke-width: 2;
    }

    .gap {
      fill: #e5e7eb;
      stroke: #6b7280;
      stroke-width: 2;
    }

    .sync {
      fill: #bfdbfe;
      stroke: #1d4ed8;
      stroke-width: 2;
    }

    .arrow {
      stroke: #374151;
      stroke-width: 2;
      marker-end: url(#arrowhead);
    }
  </style>

  <defs>
    <marker id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto">
      <polygon points="0 0, 10 3.5, 0 7"
               fill="#374151"/>
    </marker>
  </defs>

  <text x="40" y="45" class="title">
    Magnetic Frame Timing
  </text>

  <text x="40" y="100" class="label">
    Arduino Record Gate
  </text>

  <line x1="260" y1="105"
        x2="1340" y2="105"
        class="axis"/>

  <polyline points="
      260,140
      320,140
      320,70
      650,70
      650,140
      760,140
      760,70
      1090,70
      1090,140
      1340,140"
      fill="none"
      stroke="#b45309"
      stroke-width="5"/>

  <text x="400" y="60" class="small">
    RECORD = HIGH
  </text>

  <text x="820" y="60" class="small">
    RECORD = HIGH
  </text>

  <text x="40" y="210" class="label">
    Tape Track 1: Mic 1
  </text>

  <rect x="260" y="180"
        width="60"
        height="55"
        class="gap"/>

  <rect x="320" y="180"
        width="330"
        height="55"
        class="audio"/>

  <rect x="650" y="180"
        width="110"
        height="55"
        class="gap"/>

  <rect x="760" y="180"
        width="330"
        height="55"
        class="audio"/>

  <rect x="1090" y="180"
        width="250"
        height="55"
        class="gap"/>

  <text x="420" y="215" class="label">
    Mic 1 Audio Frame
  </text>

  <text x="860" y="215" class="label">
    Mic 1 Audio Frame
  </text>

  <text x="40" y="300" class="label">
    Tape Track 2: Mic 2
  </text>

  <rect x="260" y="270"
        width="60"
        height="55"
        class="gap"/>

  <rect x="320" y="270"
        width="330"
        height="55"
        class="audio"/>

  <rect x="650" y="270"
        width="110"
        height="55"
        class="gap"/>

  <rect x="760" y="270"
        width="330"
        height="55"
        class="audio"/>

  <rect x="1090" y="270"
        width="250"
        height="55"
        class="gap"/>

  <text x="420" y="305" class="label">
    Mic 2 Audio Frame
  </text>

  <text x="860" y="305" class="label">
    Mic 2 Audio Frame
  </text>

  <text x="40" y="390" class="label">
    Sync / Frame Marker
  </text>

  <rect x="260" y="360"
        width="70"
        height="55"
        class="gap"/>

  <rect x="330" y="360"
        width="70"
        height="55"
        class="sync"/>

  <rect x="400" y="360"
        width="360"
        height="55"
        class="gap"/>

  <rect x="760" y="360"
        width="70"
        height="55"
        class="sync"/>

  <rect x="830" y="360"
        width="510"
        height="55"
        class="gap"/>

  <text x="335" y="395" class="small">
    SYNC
  </text>

  <text x="765" y="395" class="small">
    SYNC
  </text>

  <line x1="320" y1="470"
        x2="650" y2="470"
        class="arrow"/>

  <text x="390" y="500" class="small">
    Audio Frame
  </text>

  <line x1="650" y1="530"
        x2="760" y2="530"
        class="arrow"/>

  <text x="665" y="560" class="small">
    Guard Gap
  </text>

  <line x1="760" y1="470"
        x2="1090" y2="470"
        class="arrow"/>

  <text x="830" y="500" class="small">
    Audio Frame
  </text>

</svg>
import React, { useState } from 'react';
import { AlertCircle, TrendingUp, Target, Zap, Award } from 'lucide-react';

export default function GTAAssessment() {
  const [step, setStep] = useState('form');
  const [formData, setFormData] = useState({
    rank: '',
    timePlayed: '',
    liquidCash: '',
    totalIncome: '',

    // Stats (0-5)
    strength: '',
    flying: '',
    shooting: '',
    stamina: '',

    // Kosatka
    hasKosatka: false,
    hasSparrow: false,
    cayoCompletions: '',

    // Agency
    hasAgency: false,
    dreContractDone: false,
    securityContractsDone: '', // NEW: for Agency safe passive

    // Acid Lab
    hasAcidLab: false,
    acidLabUpgraded: false,

    // Nightclub + Feeder Businesses
    hasNightclub: false,
    nightclubTechs: '',
    nightclubFeederBusinesses: [], // NEW: track which feeders exist

    // Bunker
    hasBunker: false,
    bunkerUpgraded: false,

    // MC Businesses
    hasCocaine: false,
    hasMeth: false,
    hasCounterfeit: false,

    // Cargo Warehouse
    hasCargoWarehouse: false,

    // Vehicles
    primaryTravel: 'car',
    hasArmoredKuruma: false,

    // Playstyle
    playMode: 'solo', // NEW: solo vs crew
    preferredActivity: 'heist' // heist, passive, mixed
  });

  const [results, setResults] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFeederBusinessToggle = (business) => {
    setFormData(prev => ({
      ...prev,
      nightclubFeederBusinesses: prev.nightclubFeederBusinesses.includes(business)
        ? prev.nightclubFeederBusinesses.filter(b => b !== business)
        : [...prev.nightclubFeederBusinesses, business]
    }));
  };

  const calculateAssessment = () => {
    let score = 0;
    let breakdown = {
      stats: 0,
      passive: 0,
      active: 0,
      travel: 0,
      economic: 0
    };
    let bottlenecks = [];
    let actionPlan = [];

    const rank = parseInt(formData.rank) || 0;
    const timePlayed = parseInt(formData.timePlayed) || 1;
    const totalIncome = parseInt(formData.totalIncome) || 0;
    const incomePerHour = totalIncome / timePlayed;

    // CATEGORY 1: STATS (20 points)
    const strength = parseInt(formData.strength) || 0;
    const flying = parseInt(formData.flying) || 0;
    const shooting = parseInt(formData.shooting) || 0;
    const stamina = parseInt(formData.stamina) || 0;

    breakdown.stats += strength >= 4 ? 6 : strength >= 3 ? 4 : strength >= 2 ? 2 : 0;
    breakdown.stats += flying >= 4 ? 6 : flying >= 3 ? 4 : flying >= 2 ? 2 : 0;
    breakdown.stats += shooting >= 3 ? 4 : shooting >= 2 ? 2 : 1;
    breakdown.stats += stamina >= 4 ? 3 : stamina >= 3 ? 2 : 1;
    breakdown.stats += 1; // Base lung capacity

    if (strength < 3) {
      bottlenecks.push({
        critical: true,
        issue: 'CRITICAL: Strength at ' + strength + '/5',
        impact: 'You take massive damage in combat and climb slowly',
        fix: 'Pier Pressure mission → beach punching for 20-25 minutes',
        priority: 1
      });
    }

    if (flying < 3) {
      bottlenecks.push({
        critical: true,
        issue: 'CRITICAL: Flying at ' + flying + '/5',
        impact: 'Sparrow/Buzzard wobbles, wastes time on landings',
        fix: 'Flight School at LSIA → complete first 5-7 lessons',
        priority: 1
      });
    }

    // CATEGORY 2: PASSIVE INCOME (30 points) - REBALANCED
    let passiveIncomePerHour = 0;

    // Nightclub (0-12 points) - Now properly weighted
    if (formData.hasNightclub) {
      const techs = parseInt(formData.nightclubTechs) || 0;
      const feeders = formData.nightclubFeederBusinesses.length;

      if (techs >= 5 && feeders >= 5) {
        breakdown.passive += 12;
        passiveIncomePerHour += 50000; // ~$50k/hr with all 5 feeders
      } else if (techs >= 4 && feeders >= 4) {
        breakdown.passive += 9;
        passiveIncomePerHour += 40000;
      } else if (techs >= 3 && feeders >= 3) {
        breakdown.passive += 6;
        passiveIncomePerHour += 30000;
      } else {
        breakdown.passive += 3;
        passiveIncomePerHour += 15000;
        bottlenecks.push({
          critical: false,
          issue: 'Nightclub underutilized',
          impact: 'Missing ~$35k+/hr passive - need 5 feeder businesses',
          fix: 'Own Bunker + Cargo + Coke + Meth + Cash, assign all 5 techs',
          priority: 2
        });
      }
    } else {
      bottlenecks.push({
        critical: false,
        issue: 'No Nightclub',
        impact: 'Missing best passive income ($50k/hr potential)',
        fix: 'Buy Nightclub when you have $1.5M+ and feeder businesses',
        priority: 3
      });
    }

    // Agency Safe (0-8 points) - NEW: Properly counted as passive
    if (formData.hasAgency) {
      const securityContracts = parseInt(formData.securityContractsDone) || 0;
      if (formData.dreContractDone && securityContracts >= 200) {
        breakdown.passive += 8;
        passiveIncomePerHour += 25000; // Max $25k/hr passive
      } else if (formData.dreContractDone && securityContracts >= 100) {
        breakdown.passive += 6;
        passiveIncomePerHour += 20000;
      } else if (formData.dreContractDone) {
        breakdown.passive += 4;
        passiveIncomePerHour += 15000;
        bottlenecks.push({
          critical: false,
          issue: 'Agency safe not maxed',
          impact: 'Only generating ~$15k/hr - max is $25k/hr',
          fix: 'Complete more Security Contracts (need 200+ total)',
          priority: 3
        });
      } else {
        breakdown.passive += 1;
      }
    }

    // Acid Lab (0-6 points) - ADJUSTED
    if (formData.hasAcidLab) {
      if (formData.acidLabUpgraded) {
        breakdown.passive += 6;
        passiveIncomePerHour += 80000; // ~$80k/hr upgraded
      } else {
        breakdown.passive += 3;
        passiveIncomePerHour += 40000;
        bottlenecks.push({
          critical: false,
          issue: 'Acid Lab not upgraded',
          impact: 'Only $40k/hr - upgrade adds another $40k/hr',
          fix: 'Complete 10 Fooligan Jobs (call Dax) → buy Equipment Upgrade',
          priority: 2
        });
      }
    } else {
      bottlenecks.push({
        critical: false,
        issue: 'No Acid Lab',
        impact: 'Missing $80k/hr passive income',
        fix: 'Buy Acid Lab when you have $750k',
        priority: 3
      });
    }

    // Bunker (0-4 points)
    if (formData.hasBunker) {
      breakdown.passive += formData.bunkerUpgraded ? 4 : 2;
      passiveIncomePerHour += formData.bunkerUpgraded ? 60000 : 30000;
    }

    // CATEGORY 3: ACTIVE GRINDING (25 points)
    let activeIncomePerHour = 0;

    if (formData.hasKosatka) {
      const cayoRuns = parseInt(formData.cayoCompletions) || 0;

      if (formData.hasSparrow) {
        if (cayoRuns >= 20) {
          breakdown.active += 15;
          // Expert: 45-min runs = $1.3M avg = $1.73M/hr (with 144-min cooldown factored)
          activeIncomePerHour += 900000; 
        } else if (cayoRuns >= 10) {
          breakdown.active += 13;
          activeIncomePerHour += 800000;
        } else if (cayoRuns >= 5) {
          breakdown.active += 10;
          activeIncomePerHour += 700000;
        } else if (cayoRuns >= 1) {
          breakdown.active += 8;
          activeIncomePerHour += 600000;
        } else {
          breakdown.active += 5;
          bottlenecks.push({
            critical: true,
            issue: 'Kosatka + Sparrow owned but Cayo never completed',
            impact: 'Wasted $2.2M investment sitting idle',
            fix: 'Complete first Cayo Perico TONIGHT - $1.1M first-time bonus',
            priority: 1
          });
        }
      } else {
        breakdown.active += 3;
        bottlenecks.push({
          critical: true,
          issue: 'Kosatka without Sparrow',
          impact: 'Setup takes 90+ min instead of 45 - wastes massive time',
          fix: 'Buy Sparrow ASAP ($1.8M) - mandatory for efficient Cayo',
          priority: 1
        });
      }
    } else {
      bottlenecks.push({
        critical: true,
        issue: 'No Kosatka',
        impact: 'Missing best solo money maker ($900k+/hr potential)',
        fix: 'Save $2.2M for Kosatka + Sparrow bundle',
        priority: 2
      });
    }

    // Agency Active Income (Payphone Hits)
    if (formData.hasAgency && formData.dreContractDone) {
      breakdown.active += 7;
      activeIncomePerHour += 200000; // $85k per 20-min call = ~$255k/hr, mix with other activities

      if (!formData.dreContractDone) {
        bottlenecks.push({
          critical: false,
          issue: 'Dr. Dre Contract not completed',
          impact: 'Missing $1M payout + Payphone Hits ($85k per 20 min)',
          fix: 'Complete Dr. Dre Contract (5-7 missions, ~3 hours total)',
          priority: 2
        });
      }
    } else if (formData.hasAgency) {
      breakdown.active += 2;
      bottlenecks.push({
        critical: false,
        issue: 'Dr. Dre Contract not completed',
        impact: 'Missing $1M payout + Payphone Hits unlock',
        fix: 'Complete Dr. Dre Contract (5-7 missions)',
        priority: 2
      });
    } else {
      bottlenecks.push({
        critical: false,
        issue: 'No Agency',
        impact: 'Missing Payphone Hits ($200k+/hr active) + $25k/hr passive',
        fix: 'Buy Agency when you have $2M+',
        priority: 3
      });
    }

    breakdown.active += 3; // Base weapons/missions access

    // CATEGORY 4: TRAVEL (15 points)
    if (formData.primaryTravel === 'sparrow' || formData.primaryTravel === 'oppressor') {
      breakdown.travel += 9;
    } else if (formData.primaryTravel === 'buzzard') {
      breakdown.travel += 7;
    } else if (formData.primaryTravel === 'mixed') {
      breakdown.travel += 4;
    } else {
      breakdown.travel += 0;
      bottlenecks.push({
        critical: true,
        issue: 'No air travel',
        impact: 'Massive time waste - 5+ min per mission vs 1 min',
        fix: 'Use Sparrow (if owned) or request CEO Buzzard',
        priority: 1
      });
    }

    if (formData.hasArmoredKuruma) {
      breakdown.travel += 6;
    } else {
      bottlenecks.push({
        critical: false,
        issue: 'No Armored Kuruma',
        impact: 'Will die repeatedly in contact missions and heist setups',
        fix: 'Buy Armored Kuruma ($525k) - bulletproof for PvE',
        priority: 2
      });
    }

    // CATEGORY 5: ECONOMIC (10 points) - REDUCED from 15
    if (incomePerHour >= 300000) breakdown.economic += 4;
    else if (incomePerHour >= 200000) breakdown.economic += 3;
    else if (incomePerHour >= 150000) breakdown.economic += 2;
    else if (incomePerHour >= 100000) breakdown.economic += 1;

    const liquidCash = parseInt(formData.liquidCash) || 0;
    if (liquidCash > 2000000) breakdown.economic += 3;
    else if (liquidCash > 1000000) breakdown.economic += 2;
    else breakdown.economic += 1;

    if (rank >= 135) breakdown.economic += 3;
    else if (rank >= 100) breakdown.economic += 2;
    else if (rank >= 50) breakdown.economic += 1;

    // Total score
    score = breakdown.stats + breakdown.passive + breakdown.active + breakdown.travel + breakdown.economic;

    // Calculate true earning potential
    const totalEarningPotential = passiveIncomePerHour + activeIncomePerHour;

    // Determine tier
    let tier = '';
    let tierColor = '';
    let tierDescription = '';

    if (score >= 85) {
      tier = 'S - The Kingpin';
      tierColor = 'text-yellow-400';
      tierDescription = '$1.5M+/hr potential - You run the game';
    } else if (score >= 75 && timePlayed < 100) {
      tier = 'A+ - The Sprinter';
      tierColor = 'text-green-400';
      tierDescription = '$1M-1.5M/hr - Elite early progression';
    } else if (score >= 70) {
      tier = 'A - The Professional';
      tierColor = 'text-green-400';
      tierDescription = '$800k-1.2M/hr - Solid foundation';
    } else if (score >= 55) {
      tier = 'B - The Hustler';
      tierColor = 'text-blue-400';
      tierDescription = '$400k-700k/hr - Working for it';
    } else if (score >= 35) {
      tier = 'C - The Employee';
      tierColor = 'text-purple-400';
      tierDescription = '$150k-400k/hr - Early grind phase';
    } else if (score >= 20) {
      tier = 'D - The Victim';
      tierColor = 'text-orange-400';
      tierDescription = '$50k-150k/hr - Knowledge gap';
    } else {
      tier = 'F - The Bleeder';
      tierColor = 'text-red-400';
      tierDescription = 'Negative income - Needs restructuring';
    }

    // Sort bottlenecks by priority
    bottlenecks.sort((a, b) => a.priority - b.priority);

    // Generate action plan
    actionPlan.push({
      phase: 'TONIGHT (30-60 min)',
      tasks: []
    });

    if (strength < 3) {
      actionPlan[0].tasks.push('Start Pier Pressure mission → punch NPCs for 20 min');
    }
    if (flying < 3) {
      actionPlan[0].tasks.push('Flight School at LSIA → complete first 5 lessons');
    }
    if (formData.hasKosatka && formData.hasSparrow && parseInt(formData.cayoCompletions) === 0) {
      actionPlan[0].tasks.push('Run your first Cayo Perico ($1.1M first-time bonus)');
    }
    if (actionPlan[0].tasks.length === 0) {
      actionPlan[0].tasks.push('Stats look good! Start your grind loop.');
    }

    actionPlan.push({
      phase: 'THIS WEEK',
      tasks: []
    });

    if (formData.hasKosatka && formData.hasSparrow && parseInt(formData.cayoCompletions) < 5) {
      const cooldownNote = formData.playMode === 'solo' ? ' (solo 144-min cooldown)' : ' (crew 48-min cooldown)';
      actionPlan[1].tasks.push('Complete 5 Cayo Perico runs' + cooldownNote);
    } else if (formData.hasKosatka && !formData.hasSparrow) {
      actionPlan[1].tasks.push('Save for Sparrow ($1.8M) - cuts Cayo time in half');
    } else if (!formData.hasKosatka) {
      actionPlan[1].tasks.push('Save for Kosatka + Sparrow ($2.2M) - essential for progression');
    }

    if (formData.hasAgency && !formData.dreContractDone) {
      actionPlan[1].tasks.push('Complete Dr. Dre Contract ($1M + Payphone Hits unlock)');
    }

    if (formData.hasAcidLab && !formData.acidLabUpgraded) {
      actionPlan[1].tasks.push('Complete 10 Fooligan Jobs → buy Acid Lab Equipment Upgrade');
    }

    if (formData.hasNightclub && formData.nightclubFeederBusinesses.length < 5) {
      actionPlan[1].tasks.push('Set up 5 feeder businesses for Nightclub (Cargo/Bunker/Coke/Meth/Cash)');
    }

    actionPlan.push({
      phase: 'HEIST LEADERSHIP READY',
      tasks: [
        'Rank 50+ (unlock more weapons/armor)',
        'Strength 3/5+ (survive combat)',
        'Flying 3/5+ (pilot reliably for crew)',
        '10+ Cayo Perico completions (know stealth routes)',
        'Armored Kuruma (protect crew in setup missions)',
        'Agency + Payphone Hits (show income optimization knowledge)'
      ]
    });

    // Estimate hours to heist ready
    let hoursToReady = 0;
    if (strength < 3) hoursToReady += 0.5;
    if (flying < 3) hoursToReady += 0.5;
    if (!formData.hasKosatka) hoursToReady += 15; // Time to earn $2.2M
    if (formData.hasKosatka && !formData.hasSparrow) hoursToReady += 8;

    const cayoRuns = parseInt(formData.cayoCompletions) || 0;
    if (cayoRuns < 10) {
      // 144 min cooldown + ~50 min per run = ~194 min per cycle
      const runsNeeded = 10 - cayoRuns;
      hoursToReady += (runsNeeded * 194 / 60);
    }

    if (rank < 50) hoursToReady += (50 - rank) * 0.3;

    setResults({
      score,
      breakdown,
      tier,
      tierColor,
      tierDescription,
      bottlenecks: bottlenecks.slice(0, 5),
      actionPlan,
      hoursToReady: Math.ceil(hoursToReady),
      incomePerHour: Math.round(incomePerHour),
      potentialIncome: Math.round(totalEarningPotential),
      passiveIncome: Math.round(passiveIncomePerHour),
      activeIncome: Math.round(activeIncomePerHour)
    });

    setStep('results');
  };

  if (step === 'results' && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Account Assessment</h1>
                <p className="text-slate-300">Rank {formData.rank} • {formData.timePlayed}hrs played</p>
              </div>
              <button
                onClick={() => setStep('form')}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
              >
                Edit Answers
              </button>
            </div>
          </div>

          {/* Tier Score */}
          <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-8 text-center">
            <Award className="w-16 h-16 mx-auto mb-4 text-yellow-400" />
            <div className="text-6xl font-bold text-white mb-2">{results.score}/100</div>
            <div className={`text-2xl font-bold mb-2 ${results.tierColor}`}>
              TIER {results.tier}
            </div>
            <div className="text-slate-300">{results.tierDescription}</div>
            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
                <div className="text-slate-400">Passive Income</div>
                <div className="text-green-400 font-bold text-lg">
                  ${(results.passiveIncome / 1000).toFixed(0)}k/hr
                </div>
              </div>
              <div className="p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <div className="text-slate-400">Active Income</div>
                <div className="text-blue-400 font-bold text-lg">
                  ${(results.activeIncome / 1000).toFixed(0)}k/hr
                </div>
              </div>
            </div>
            <div className="mt-4 text-slate-400">
              Total Potential: <span className="text-white font-bold">${(results.potentialIncome / 1000).toFixed(0)}k/hour</span>
            </div>
          </div>

          {/* Score Breakdown */}
          <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Score Breakdown</h2>
            <div className="space-y-3">
              {[
                { name: 'Character Stats', score: results.breakdown.stats, max: 20, color: 'bg-red-500' },
                { name: 'Passive Income', score: results.breakdown.passive, max: 30, color: 'bg-green-500' },
                { name: 'Active Grinding', score: results.breakdown.active, max: 25, color: 'bg-blue-500' },
                { name: 'Travel Efficiency', score: results.breakdown.travel, max: 15, color: 'bg-yellow-500' },
                { name: 'Economic', score: results.breakdown.economic, max: 10, color: 'bg-purple-500' }
              ].map((cat) => (
                <div key={cat.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300">{cat.name}</span>
                    <span className="text-white font-bold">{cat.score}/{cat.max}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`${cat.color} h-2 rounded-full transition-all duration-500`}
                      style={{ width: `${(cat.score / cat.max) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Critical Bottlenecks */}
          {results.bottlenecks.length > 0 && (
            <div className="bg-slate-800/50 backdrop-blur border border-red-500/30 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="text-red-400" />
                <h2 className="text-xl font-bold text-white">Critical Issues</h2>
              </div>
              <div className="space-y-4">
                {results.bottlenecks.map((bottleneck, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg ${
                      bottleneck.critical
                        ? 'bg-red-900/20 border border-red-500/30'
                        : 'bg-orange-900/20 border border-orange-500/30'
                    }`}
                  >
                    <div className="font-bold text-white mb-1">{bottleneck.issue}</div>
                    <div className="text-sm text-slate-300 mb-2">Impact: {bottleneck.impact}</div>
                    <div className="text-sm text-green-400">→ Fix: {bottleneck.fix}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Plan */}
          <div className="bg-slate-800/50 backdrop-blur border border-green-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="text-green-400" />
              <h2 className="text-xl font-bold text-white">Your Path to Heist Leadership</h2>
            </div>
            <div className="mb-4 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
              <div className="text-2xl font-bold text-white mb-1">
                ~{results.hoursToReady} Hours
              </div>
              <div className="text-sm text-slate-300">Real-time hours to heist-ready (spread over days due to cooldowns)</div>
            </div>

            <div className="space-y-4">
              {results.actionPlan.map((phase, idx) => (
                <div key={idx} className="border-l-4 border-green-500 pl-4">
                  <div className="font-bold text-green-400 mb-2">{phase.phase}</div>
                  <ul className="space-y-1">
                    {phase.tasks.map((task, taskIdx) => (
                      <li key={taskIdx} className="text-slate-300 text-sm flex items-start gap-2">
                        <span className="text-green-400 mt-1">→</span>
                        <span>{task}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Heist Ready Criteria */}
          <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-3">What "Heist Ready" Means</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-start gap-2">
                <Zap className="text-yellow-400 mt-1 flex-shrink-0" size={16} />
                <div>
                  <div className="text-white font-semibold">Know the Routes</div>
                  <div className="text-slate-400">10+ Cayo runs = you can guide others</div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Zap className="text-yellow-400 mt-1 flex-shrink-0" size={16} />
                <div>
                  <div className="text-white font-semibold">Can Survive</div>
                  <div className="text-slate-400">Strength 3+ = won't get one-shot</div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Zap className="text-yellow-400 mt-1 flex-shrink-0" size={16} />
                <div>
                  <div className="text-white font-semibold">Fast Travel</div>
                  <div className="text-slate-400">Air vehicle = don't waste crew's time</div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Zap className="text-yellow-400 mt-1 flex-shrink-0" size={16} />
                <div>
                  <div className="text-white font-semibold">Protect the Team</div>
                  <div className="text-slate-400">Armored Kuruma for setup missions</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">GTA Online Assessment</h1>
            <p className="text-slate-300">Get heist-ready with accurate 2026 meta analysis</p>
          </div>

          <div className="space-y-6">
            {/* Account Basics */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-white border-b border-slate-700 pb-2">Account Basics</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Rank</label>
                  <input
                    type="number"
                    value={formData.rank}
                    onChange={(e) => handleInputChange('rank', e.target.value)}
                    className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                    placeholder="30"
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Hours Played</label>
                  <input
                    type="number"
                    value={formData.timePlayed}
                    onChange={(e) => handleInputChange('timePlayed', e.target.value)}
                    className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                    placeholder="50"
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Liquid Cash ($)</label>
                  <input
                    type="number"
                    value={formData.liquidCash}
                    onChange={(e) => handleInputChange('liquidCash', e.target.value)}
                    className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                    placeholder="1990000"
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Total Income ($)</label>
                  <input
                    type="number"
                    value={formData.totalIncome}
                    onChange={(e) => handleInputChange('totalIncome', e.target.value)}
                    className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                    placeholder="9500000"
                  />
                </div>
              </div>
            </div>

            {/* Character Stats */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-white border-b border-slate-700 pb-2">Character Stats (0-5)</h2>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { key: 'strength', label: 'Strength', critical: true },
                  { key: 'flying', label: 'Flying', critical: true },
                  { key: 'shooting', label: 'Shooting', critical: false },
                  { key: 'stamina', label: 'Stamina', critical: false }
                ].map(stat => (
                  <div key={stat.key}>
                    <label className="block text-sm text-slate-300 mb-1">
                      {stat.label} {stat.critical && <span className="text-red-400">*</span>}
                    </label>
                    <select
                      value={formData[stat.key]}
                      onChange={(e) => handleInputChange(stat.key, e.target.value)}
                      className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                    >
                      <option value="">Select</option>
                      <option value="5">5/5 (Maxed)</option>
                      <option value="4">4/5</option>
                      <option value="3">3/5</option>
                      <option value="2">2/5</option>
                      <option value="1">1/5</option>
                      <option value="0">0/5</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>

            {/* Playstyle */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-white border-b border-slate-700 pb-2">Playstyle</h2>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Primary Play Mode</label>
                <select
                  value={formData.playMode}
                  onChange={(e) => handleInputChange('playMode', e.target.value)}
                  className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                >
                  <option value="solo">Solo (144-min Cayo cooldown)</option>
                  <option value="crew">With crew (48-min Cayo cooldown)</option>
                </select>
              </div>
            </div>

            {/* Major Assets */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-white border-b border-slate-700 pb-2">Major Assets</h2>

              {/* Kosatka */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.hasKosatka}
                    onChange={(e) => handleInputChange('hasKosatka', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label className="text-slate-300">Kosatka Submarine</label>
                </div>
                {formData.hasKosatka && (
                  <div className="ml-6 space-y-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.hasSparrow}
                        onChange={(e) => handleInputChange('hasSparrow', e.target.checked)}
                        className="w-4 h-4"
                      />
                      <label className="text-slate-300">Sparrow Helicopter</label>
                    </div>
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Cayo Perico Completions</label>
                      <input
                        type="number"
                        value={formData.cayoCompletions}
                        onChange={(e) => handleInputChange('cayoCompletions', e.target.value)}
                        className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                        placeholder="0"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Agency */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.hasAgency}
                    onChange={(e) => handleInputChange('hasAgency', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label className="text-slate-300">Agency</label>
                </div>
                {formData.hasAgency && (
                  <div className="ml-6 space-y-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.dreContractDone}
                        onChange={(e) => handleInputChange('dreContractDone', e.target.checked)}
                        className="w-4 h-4"
                      />
                      <label className="text-slate-300">Dr. Dre Contract Completed</label>
                    </div>
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Security Contracts Completed</label>
                      <input
                        type="number"
                        value={formData.securityContractsDone}
                        onChange={(e) => handleInputChange('securityContractsDone', e.target.value)}
                        className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                        placeholder="0 (need 200+ for max Agency safe)"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Nightclub */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.hasNightclub}
                    onChange={(e) => handleInputChange('hasNightclub', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label className="text-slate-300">Nightclub</label>
                </div>
                {formData.hasNightclub && (
                  <div className="ml-6 space-y-3">
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Technicians Assigned</label>
                      <input
                        type="number"
                        value={formData.nightclubTechs}
                        onChange={(e) => handleInputChange('nightclubTechs', e.target.value)}
                        className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                        placeholder="0-5"
                        max="5"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-slate-300 mb-2">Feeder Businesses (check all you own)</label>
                      <div className="space-y-2">
                        {[
                          { id: 'cargo', label: 'Cargo Warehouse' },
                          { id: 'bunker', label: 'Bunker' },
                          { id: 'coke', label: 'Cocaine Lockup' },
                          { id: 'meth', label: 'Meth Lab' },
                          { id: 'cash', label: 'Counterfeit Cash' }
                        ].map(business => (
                          <div key={business.id} className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.nightclubFeederBusinesses.includes(business.id)}
                              onChange={() => handleFeederBusinessToggle(business.id)}
                              className="w-4 h-4"
                            />
                            <label className="text-slate-300 text-sm">{business.label}</label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Acid Lab */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.hasAcidLab}
                    onChange={(e) => handleInputChange('hasAcidLab', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label className="text-slate-300">Acid Lab</label>
                </div>
                {formData.hasAcidLab && (
                  <div className="ml-6">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.acidLabUpgraded}
                        onChange={(e) => handleInputChange('acidLabUpgraded', e.target.checked)}
                        className="w-4 h-4"
                      />
                      <label className="text-slate-300">Equipment Upgrade</label>
                    </div>
                  </div>
                )}
              </div>

              {/* Bunker */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.hasBunker}
                    onChange={(e) => handleInputChange('hasBunker', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label className="text-slate-300">Bunker</label>
                </div>
                {formData.hasBunker && (
                  <div className="ml-6">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.bunkerUpgraded}
                        onChange={(e) => handleInputChange('bunkerUpgraded', e.target.checked)}
                        className="w-4 h-4"
                      />
                      <label className="text-slate-300">Equipment + Staff Upgrades</label>
                    </div>
                  </div>
                )}
              </div>

              {/* Armored Kuruma */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.hasArmoredKuruma}
                  onChange={(e) => handleInputChange('hasArmoredKuruma', e.target.checked)}
                  className="w-4 h-4"
                />
                <label className="text-slate-300">Armored Kuruma</label>
              </div>
            </div>

            {/* Travel */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-white border-b border-slate-700 pb-2">Travel Method</h2>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Primary Travel</label>
                <select
                  value={formData.primaryTravel}
                  onChange={(e) => handleInputChange('primaryTravel', e.target.value)}
                  className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-purple-500 focus:outline-none"
                >
                  <option value="car">Drive everywhere</option>
                  <option value="mixed">Mix of driving and flying</option>
                  <option value="buzzard">Buzzard</option>
                  <option value="sparrow">Sparrow (primary)</option>
                  <option value="oppressor">Oppressor Mk II</option>
                </select>
              </div>
            </div>

            <button
              onClick={calculateAssessment}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-4 rounded-lg transition-all transform hover:scale-105"
            >
              Calculate Assessment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

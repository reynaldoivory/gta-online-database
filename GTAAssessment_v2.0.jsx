import React, { useState } from 'react';
import { AlertCircle, Target, Zap, Award, TrendingUp, Building, Car, Sword } from 'lucide-react';

export default function GTAMetaAssessment() {
  const [step, setStep] = useState('form');
  const [formData, setFormData] = useState({
    // Account Basics
    rank: '',
    timePlayed: '',
    liquidCash: '',
    totalIncome: '',
    recentIncome: '', // Last 10 hours

    // Stats (0-5)
    strength: '',
    flying: '',
    shooting: '',
    stamina: '',
    stealth: '',
    lungCapacity: '',

    // Active Income Assets
    hasKosatka: false,
    hasSparrow: false,
    cayoCompletions: '',
    cayoAvgTime: '', // NEW: Average time in minutes
    hasAgency: false,
    dreContractDone: false,
    securityContractsDone: '', // NEW: For Agency safe
    payphoneHitsDone: '',

    // Passive Income Assets
    hasAcidLab: false,
    acidLabUpgraded: false,
    hasNightclub: false,
    nightclubTechs: '',
    nightclubLinked: [], // Feeder businesses
    hasBunker: false,
    bunkerUpgraded: false,
    hasMcCocaine: false,
    hasMcMeth: false,
    hasMcCash: false,
    hasCargoWarehouse: false,

    // Vehicles & Travel
    primaryTravel: 'car',
    hasOppressorMkII: false,
    hasArmoredKuruma: false,
    hasImaniTech: false,

    // Playstyle
    playMode: 'solo', // solo vs crew
    checksWeeklyBonuses: false,
  });

  const [results, setResults] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleLinkedToggle = (business) => {
    setFormData(prev => {
      const current = prev.nightclubLinked;
      return {
        ...prev,
        nightclubLinked: current.includes(business)
          ? current.filter(b => b !== business)
          : [...current, business]
      };
    });
  };

  const calculateAssessment = () => {
    const rank = parseInt(formData.rank) || 0;
    const timePlayed = parseInt(formData.timePlayed) || 1;
    const totalIncome = parseInt(formData.totalIncome) || 0;
    const recentIncome = parseInt(formData.recentIncome) || 0;
    const recentHours = Math.min(10, timePlayed);

    // Primary metric: recent sustainable rate
    const recentRatePerHour = recentIncome / recentHours;
    const lifetimeRatePerHour = totalIncome / timePlayed;

    let score = 0;
    let breakdown = {
      stats: { score: 0, max: 20, issues: [] },
      passive: { score: 0, max: 30, issues: [] },
      active: { score: 0, max: 25, issues: [] },
      travel: { score: 0, max: 15, issues: [] },
      economic: { score: 0, max: 10, issues: [] }
    };

    // Bottleneck tracking with deduplication
    const bottlenecks = [];
    const bottleneckCache = new Set();

    const addBottleneck = (bottleneck) => {
      if (!bottleneckCache.has(bottleneck.id)) {
        bottleneckCache.add(bottleneck.id);
        bottlenecks.push(bottleneck);
        return true;
      }
      return false;
    };

    let passiveIncomePerHour = 0;
    let activeIncomePerHour = 0;

    // ======================
    // CATEGORY 1: STATS (20 pts)
    // ======================
    const strength = parseInt(formData.strength) || 0;
    const flying = parseInt(formData.flying) || 0;
    const shooting = parseInt(formData.shooting) || 0;
    const stamina = parseInt(formData.stamina) || 0;
    const stealth = parseInt(formData.stealth) || 0;
    const lung = parseInt(formData.lungCapacity) || 0;

    breakdown.stats.score += strength >= 4 ? 6 : strength >= 3 ? 4 : strength >= 2 ? 2 : 0;
    if (strength < 3) {
      addBottleneck({
        id: 'low-strength',
        critical: true,
        issue: `Strength: ${strength}/5`,
        impact: 'Massive damage taken, slow climbing',
        fix: 'Pier Pressure mission beach punching (20-25 min)',
        time: 0.5,
        priority: 1,
        category: 'stats'
      });
      breakdown.stats.issues.push('Low Strength');
    }

    breakdown.stats.score += flying >= 4 ? 6 : flying >= 3 ? 4 : flying >= 2 ? 2 : 0;
    if (flying < 3) {
      addBottleneck({
        id: 'low-flying',
        critical: true,
        issue: `Flying: ${flying}/5`,
        impact: 'Helicopter wobble, wasted time landing',
        fix: 'Flight School at LSIA - first 5 lessons (25 min)',
        time: 0.5,
        priority: 1,
        category: 'stats'
      });
      breakdown.stats.issues.push('Low Flying');
    }

    breakdown.stats.score += shooting >= 4 ? 3 : shooting >= 3 ? 2 : 1;
    breakdown.stats.score += stamina >= 4 ? 3 : stamina >= 3 ? 2 : 1;
    breakdown.stats.score += lung >= 3 ? 2 : 1;

    // ======================
    // CATEGORY 2: PASSIVE INCOME (30 pts)
    // ======================

    // Nightclub - PASSIVE KING (15 pts max)
    if (formData.hasNightclub) {
      const techs = parseInt(formData.nightclubTechs) || 0;
      const feeders = formData.nightclubLinked.length;

      let nightclubScore = 0;
      if (techs >= 5 && feeders >= 5) {
        nightclubScore = 15;
        passiveIncomePerHour += 50000;
      } else if (techs >= 4 && feeders >= 4) {
        nightclubScore = 11;
        passiveIncomePerHour += 40000;
      } else if (techs >= 3 && feeders >= 3) {
        nightclubScore = 7;
        passiveIncomePerHour += 30000;
      } else if (techs >= 1) {
        nightclubScore = 3;
        passiveIncomePerHour += 15000;
      } else {
        nightclubScore = 1;
      }

      breakdown.passive.score += nightclubScore;

      if (techs < 5 || feeders < 5) {
        addBottleneck({
          id: 'nightclub-underused',
          critical: false,
          issue: 'Nightclub not fully optimized',
          impact: `Missing ~$${Math.round((50000 - (passiveIncomePerHour > 0 ? Math.min(passiveIncomePerHour, 50000) : 0)) / 1000)}k/hr passive`,
          fix: 'Link 5 businesses (Cargo/Bunker/Coke/Meth/Cash) + assign 5 techs',
          time: 3,
          priority: 2,
          category: 'passive'
        });
        breakdown.passive.issues.push('Nightclub incomplete');
      }
    } else {
      addBottleneck({
        id: 'no-nightclub',
        critical: false,
        issue: 'No Nightclub',
        impact: 'Missing best passive income ($50k/hr potential)',
        fix: 'Buy Nightclub after owning feeder businesses ($1.5M+)',
        time: 15,
        priority: 3,
        category: 'passive'
      });
    }

    // Agency Safe Passive (8 pts max)
    const securityContracts = parseInt(formData.securityContractsDone) || 0;
    if (formData.hasAgency && formData.dreContractDone && securityContracts > 0) {
      let agencySafeScore = 0;
      let agencySafeIncome = 0;

      if (securityContracts >= 200) {
        agencySafeScore = 8;
        agencySafeIncome = 25000;
      } else if (securityContracts >= 100) {
        agencySafeScore = 6;
        agencySafeIncome = 20000;
      } else if (securityContracts >= 50) {
        agencySafeScore = 4;
        agencySafeIncome = 15000;
      } else {
        agencySafeScore = 2;
        agencySafeIncome = 10000;
      }

      breakdown.passive.score += agencySafeScore;
      passiveIncomePerHour += agencySafeIncome;

      if (securityContracts < 200) {
        breakdown.passive.issues.push('Agency safe not maxed');
      }
    }

    // Acid Lab (7 pts max)
    if (formData.hasAcidLab) {
      if (formData.acidLabUpgraded) {
        breakdown.passive.score += 7;
        passiveIncomePerHour += 80000;
      } else {
        breakdown.passive.score += 4;
        passiveIncomePerHour += 40000;
        addBottleneck({
          id: 'acid-lab-basic',
          critical: false,
          issue: 'Acid Lab not upgraded',
          impact: 'Only $40k/hr - upgrade adds $40k/hr more',
          fix: 'Complete 10 Fooligan Jobs → buy Equipment Upgrade',
          time: 2,
          priority: 2,
          category: 'passive'
        });
      }
    } else {
      addBottleneck({
        id: 'no-acid-lab',
        critical: false,
        issue: 'No Acid Lab',
        impact: 'Missing easiest passive to set up ($80k/hr)',
        fix: 'Buy Acid Lab when you have $750k',
        time: 10,
        priority: 3,
        category: 'passive'
      });
    }

    // Bunker (5 pts max)
    if (formData.hasBunker) {
      if (formData.bunkerUpgraded) {
        breakdown.passive.score += 5;
        passiveIncomePerHour += 60000;
      } else {
        breakdown.passive.score += 2;
        passiveIncomePerHour += 30000;
      }
    }

    // ======================
    // CATEGORY 3: ACTIVE INCOME (25 pts)
    // ======================

    // Cayo Perico - EFFICIENCY-WEIGHTED (12 pts max)
    if (formData.hasKosatka) {
      const cayoRuns = parseInt(formData.cayoCompletions) || 0;
      const cayoTime = parseInt(formData.cayoAvgTime) || 120;

      let cayoScore = 3; // Base Kosatka
      let cayoIncome = 0;

      if (formData.hasSparrow) {
        cayoScore += 2; // Sparrow bonus

        // EFFICIENCY TIERS (Your key insight)
        if (cayoTime <= 50 && cayoRuns >= 5) {
          cayoScore += 10; // Elite mastery
          cayoIncome = 900000;
        } else if (cayoTime <= 65 && cayoRuns >= 3) {
          cayoScore += 6; // Pro
          cayoIncome = 750000;
        } else if (cayoTime <= 85 && cayoRuns >= 1) {
          cayoScore += 4; // Competent
          cayoIncome = 600000;
        } else if (cayoRuns >= 1) {
          cayoScore += 2; // Completed but slow
          cayoIncome = 450000;
        }

        if (cayoRuns === 0) {
          addBottleneck({
            id: 'cayo-unused',
            critical: true,
            issue: 'Kosatka + Sparrow unused',
            impact: '$2.2M investment sitting idle',
            fix: 'Complete first Cayo run TONIGHT ($1.1M bonus)',
            time: 1.5,
            priority: 1,
            category: 'active'
          });
        }
      } else {
        addBottleneck({
          id: 'no-sparrow',
          critical: true,
          issue: 'Kosatka without Sparrow',
          impact: 'Setup takes 90+ min instead of 45',
          fix: 'Buy Sparrow ($1.8M) after next Cayo',
          time: 2,
          priority: 1,
          category: 'active'
        });
      }

      breakdown.active.score += Math.min(cayoScore, 15); // Cap at 15
      activeIncomePerHour += cayoIncome;
    } else {
      addBottleneck({
        id: 'no-kosatka',
        critical: true,
        issue: 'No Kosatka submarine',
        impact: 'Missing best solo active income ($900k+/hr)',
        fix: 'Save $2.2M for Kosatka (top priority)',
        time: 12,
        priority: 1,
        category: 'active'
      });
    }

    // Agency + Payphone Hits (8 pts max)
    if (formData.hasAgency) {
      let agencyScore = 2; // Base

      if (formData.dreContractDone) {
        agencyScore += 2; // Dre completion

        const payphoneHits = parseInt(formData.payphoneHitsDone) || 0;
        if (payphoneHits >= 10) {
          agencyScore += 4;
          activeIncomePerHour += 255000; // $85k per 20min
        } else if (payphoneHits >= 5) {
          agencyScore += 3;
          activeIncomePerHour += 200000;
        } else if (payphoneHits >= 1) {
          agencyScore += 1;
          activeIncomePerHour += 150000;
        }
      } else {
        addBottleneck({
          id: 'dre-incomplete',
          critical: false,
          issue: 'Dr. Dre Contract incomplete',
          impact: 'Missing $1M payout + Payphone Hits',
          fix: 'Complete Dre Contract (5-7 missions, ~3 hrs)',
          time: 3.5,
          priority: 2,
          category: 'active'
        });
      }

      breakdown.active.score += agencyScore;
    } else {
      addBottleneck({
        id: 'no-agency',
        critical: false,
        issue: 'No Agency',
        impact: 'Missing Payphone Hits + passive safe',
        fix: 'Buy Agency when you have $2M+',
        time: 15,
        priority: 3,
        category: 'active'
      });
    }

    // Weekly Bonus Awareness (2 pts)
    breakdown.active.score += formData.checksWeeklyBonuses ? 2 : 0;

    // ======================
    // CATEGORY 4: TRAVEL (15 pts)
    // ======================
    switch (formData.primaryTravel) {
      case 'oppressor':
        breakdown.travel.score += 10;
        break;
      case 'sparrow':
        breakdown.travel.score += 9;
        break;
      case 'buzzard':
        breakdown.travel.score += 7;
        break;
      case 'mixed':
        breakdown.travel.score += 4;
        break;
      default:
        addBottleneck({
          id: 'slow-travel',
          critical: false,
          issue: 'No air travel',
          impact: 'Wasting 5-10 min per mission',
          fix: 'Use Sparrow if owned, or CEO Buzzard',
          time: 1,
          priority: 2,
          category: 'travel'
        });
    }

    // Combat Vehicle (5 pts)
    if (formData.hasOppressorMkII || formData.hasImaniTech) {
      breakdown.travel.score += 5;
    } else if (formData.hasArmoredKuruma) {
      breakdown.travel.score += 4;
    } else {
      addBottleneck({
        id: 'no-armored-vehicle',
        critical: false,
        issue: 'No armored/combat vehicle',
        impact: 'Dying repeatedly in missions',
        fix: 'Buy Armored Kuruma ($525k)',
        time: 3,
        priority: 3,
        category: 'travel'
      });
    }

    // ======================
    // CATEGORY 5: ECONOMIC (10 pts)
    // ======================
    if (recentRatePerHour >= 500000) breakdown.economic.score += 5;
    else if (recentRatePerHour >= 300000) breakdown.economic.score += 4;
    else if (recentRatePerHour >= 200000) breakdown.economic.score += 3;
    else if (recentRatePerHour >= 100000) breakdown.economic.score += 2;
    else breakdown.economic.score += 1;

    const liquidCash = parseInt(formData.liquidCash) || 0;
    const retentionRate = totalIncome > 0 ? liquidCash / totalIncome : 0;

    if (retentionRate >= 0.3) breakdown.economic.score += 3;
    else if (retentionRate >= 0.15) breakdown.economic.score += 2;
    else breakdown.economic.score += 1;

    if (rank >= 135) breakdown.economic.score += 2;
    else if (rank >= 100) breakdown.economic.score += 1;

    // ======================
    // CALCULATE TOTAL SCORE
    // ======================
    score = 
      breakdown.stats.score + 
      breakdown.passive.score + 
      breakdown.active.score + 
      breakdown.travel.score + 
      breakdown.economic.score;

    // ======================
    // DETERMINE TIER
    // ======================
    let tier, tierColor, tierDescription, incomePotential;

    if (score >= 85) {
      tier = 'S - The Kingpin';
      tierColor = 'text-yellow-400';
      tierDescription = 'Full diversified empire';
      incomePotential = '$1.5M+/hr';
    } else if (score >= 75 && timePlayed < 100) {
      tier = 'A+ - The Sprinter';
      tierColor = 'text-green-400';
      tierDescription = 'Elite early progression';
      incomePotential = '$900k-1.2M/hr';
    } else if (score >= 70) {
      tier = 'A - The Professional';
      tierColor = 'text-green-400';
      tierDescription = 'Solid active/passive mix';
      incomePotential = '$700k-900k/hr';
    } else if (score >= 55) {
      tier = 'B - The Hustler';
      tierColor = 'text-blue-400';
      tierDescription = 'Working hard, needs optimization';
      incomePotential = '$400k-700k/hr';
    } else if (score >= 35) {
      tier = 'C - The Employee';
      tierColor = 'text-purple-400';
      tierDescription = 'Foundation building phase';
      incomePotential = '$150k-400k/hr';
    } else if (score >= 20) {
      tier = 'D - The Victim';
      tierColor = 'text-orange-400';
      tierDescription = 'Information gap';
      incomePotential = '$50k-150k/hr';
    } else {
      tier = 'F - The Bleeder';
      tierColor = 'text-red-400';
      tierDescription = 'Losing money';
      incomePotential = 'Negative';
    }

    // ======================
    // BUILD 3-TIER ACTION PLAN
    // ======================
    const actionPlan = {
      immediate: [],
      shortTerm: [],
      longTerm: []
    };

    bottlenecks.sort((a, b) => a.priority - b.priority);

    bottlenecks.forEach(bottleneck => {
      const task = {
        title: bottleneck.fix,
        reason: bottleneck.issue,
        hours: bottleneck.time || 1
      };

      if (bottleneck.time <= 1) {
        actionPlan.immediate.push(task);
      } else if (bottleneck.time <= 5) {
        actionPlan.shortTerm.push(task);
      } else {
        actionPlan.longTerm.push(task);
      }
    });

    // Calculate timeline
    let activeHoursNeeded = 0;
    if (strength < 3) activeHoursNeeded += 0.5;
    if (flying < 3) activeHoursNeeded += 0.5;
    if (!formData.hasKosatka) activeHoursNeeded += 10;
    if (formData.hasKosatka && !formData.hasSparrow) activeHoursNeeded += 5;
    if (formData.hasAgency && !formData.dreContractDone) activeHoursNeeded += 4;

    const cayoRuns = parseInt(formData.cayoCompletions) || 0;
    if (cayoRuns < 10) {
      const runsNeeded = 10 - cayoRuns;
      activeHoursNeeded += (runsNeeded * 3.2);
    }

    const cooldownNote = formData.playMode === 'solo' 
      ? '144 minutes (2h24m) between solo runs'
      : '48 minutes between crew runs';

    setResults({
      score,
      breakdown,
      tier,
      tierColor,
      tierDescription,
      incomePotential,
      bottlenecks: bottlenecks.slice(0, 6),
      actionPlan,
      activeHoursNeeded: Math.ceil(activeHoursNeeded),
      recentRatePerHour: Math.round(recentRatePerHour),
      lifetimeRatePerHour: Math.round(lifetimeRatePerHour),
      passiveIncomePerHour: Math.round(passiveIncomePerHour),
      activeIncomePerHour: Math.round(activeIncomePerHour),
      cayoCooldownNote: cooldownNote
    });

    setStep('results');
  };

  // Helper: Generate personalized loop
  const generatePersonalizedLoop = () => {
    if (!results) return [];

    const steps = [];

    // Step 1: Primary income
    if (formData.hasKosatka && parseInt(formData.cayoCompletions) > 0) {
      const cooldown = formData.playMode === 'solo' ? '144-min' : '48-min';
      steps.push({
        num: 1,
        action: 'Run Cayo Perico',
        detail: `(${cooldown} cooldown)`,
        color: 'green'
      });
    } else if (formData.hasKosatka) {
      steps.push({
        num: 1,
        action: 'Complete first Cayo Perico',
        detail: '$1.1M first-time bonus',
        color: 'green'
      });
    } else {
      steps.push({
        num: 1,
        action: 'Save for Kosatka + Sparrow',
        detail: '$2.2M (top priority)',
        color: 'red'
      });
    }

    // Step 2: Cooldown filler
    if (formData.hasAgency && formData.dreContractDone) {
      steps.push({
        num: 2,
        action: 'Payphone Hits during cooldown',
        detail: '$85k per 20 minutes',
        color: 'blue'
      });
    } else if (formData.hasAgency) {
      steps.push({
        num: 2,
        action: 'Complete Dr. Dre Contract',
        detail: 'Unlocks Payphone Hits',
        color: 'yellow'
      });
    }

    // Step 3: Passive collections
    const passiveSources = [];
    if (formData.hasNightclub && parseInt(formData.nightclubTechs) >= 3) {
      passiveSources.push('Nightclub');
    }
    if (formData.hasAcidLab && formData.acidLabUpgraded) {
      passiveSources.push('Acid Lab');
    }
    if (formData.hasBunker && formData.bunkerUpgraded) {
      passiveSources.push('Bunker');
    }

    if (passiveSources.length > 0) {
      steps.push({
        num: 3,
        action: 'Collect passive sales',
        detail: passiveSources.join(', '),
        color: 'purple'
      });
    }

    return steps;
  };

  // Results Display
  if (step === 'results' && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950 p-4 md:p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold text-white">2026 Meta Assessment</h1>
                <p className="text-gray-400 mt-1">Rank {formData.rank} • {formData.timePlayed} hours</p>
              </div>
              <button
                onClick={() => setStep('form')}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition">
                Edit Assessment
              </button>
            </div>
          </div>

          {/* Score & Income */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
              <div className="flex items-center gap-4 mb-6">
                <Award className="w-12 h-12 text-yellow-400" />
                <div>
                  <div className="text-5xl font-bold text-white">{results.score}<span className="text-2xl text-gray-400">/100</span></div>
                  <div className={\`text-xl font-bold mt-2 \${results.tierColor}\`}>{results.tier}</div>
                  <div className="text-gray-300 text-sm">{results.tierDescription}</div>
                </div>
              </div>
              <div className="text-sm text-gray-400">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  <span>Cayo: {results.cayoCooldownNote}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
              <h2 className="text-xl font-bold text-white mb-4">Income Breakdown</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-green-900/20 border border-green-700/30 rounded-lg">
                  <span className="text-gray-300">Sustainable (last 10h)</span>
                  <span className="text-green-400 font-bold">${(results.recentRatePerHour / 1000).toFixed(0)}k/hr</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
                  <span className="text-gray-300">Active Potential</span>
                  <span className="text-blue-400 font-bold">${(results.activeIncomePerHour / 1000).toFixed(0)}k/hr</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-900/20 border border-purple-700/30 rounded-lg">
                  <span className="text-gray-300">Passive Potential</span>
                  <span className="text-purple-400 font-bold">${(results.passiveIncomePerHour / 1000).toFixed(0)}k/hr</span>
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-500">
                ~{results.activeHoursNeeded} active hours to heist-ready
              </div>
            </div>
          </div>

          {/* Score Breakdown */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-6">Score Breakdown</h2>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {Object.entries(results.breakdown).map(([category, data]) => (
                <div key={category} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300 capitalize">{category}</span>
                    <span className="text-white font-bold">{data.score}/{data.max}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-700"
                      style={{ 
                        width: \`\${(data.score / data.max) * 100}%\`,
                        backgroundColor: category === 'passive' ? '#10b981' :
                                        category === 'active' ? '#3b82f6' :
                                        category === 'stats' ? '#ef4444' :
                                        category === 'travel' ? '#f59e0b' : '#8b5cf6'
                      }}
                    />
                  </div>
                  {data.issues && data.issues.length > 0 && (
                    <div className="text-xs text-gray-400">
                      {data.issues.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Bottlenecks */}
          {results.bottlenecks.length > 0 && (
            <div className="bg-gray-800/50 backdrop-blur-sm border border-red-900/30 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <AlertCircle className="w-8 h-8 text-red-400" />
                <h2 className="text-xl font-bold text-white">Critical Bottlenecks</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.bottlenecks.map((bottleneck, idx) => (
                  <div 
                    key={idx}
                    className={\`p-4 rounded-xl \${
                      bottleneck.critical 
                        ? 'bg-red-900/20 border border-red-700/30' 
                        : 'bg-orange-900/20 border border-orange-700/30'
                    }\`}
                  >
                    <div className="font-bold text-white mb-2">{bottleneck.issue}</div>
                    <div className="text-sm text-gray-300 mb-3">{bottleneck.impact}</div>
                    <div className="text-sm text-green-400 font-medium">→ {bottleneck.fix}</div>
                    <div className="text-xs text-gray-500 mt-2">
                      {bottleneck.time}hr • {bottleneck.category}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Plan */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Target className="w-8 h-8 text-green-400" />
              <h2 className="text-xl font-bold text-white">Action Plan</h2>
            </div>

            {results.actionPlan.immediate.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold text-green-400 mb-3">TONIGHT (Under 1 hour)</h3>
                <div className="space-y-2 ml-4">
                  {results.actionPlan.immediate.map((item, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                      <div>
                        <div className="text-white">{item.title}</div>
                        <div className="text-sm text-gray-400">{item.reason}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.actionPlan.shortTerm.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold text-blue-400 mb-3">THIS WEEK</h3>
                <div className="space-y-2 ml-4">
                  {results.actionPlan.shortTerm.map((item, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                      <div>
                        <div className="text-white">{item.title}</div>
                        <div className="text-sm text-gray-400">{item.reason} • ~{item.hours}hr</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {results.actionPlan.longTerm.length > 0 && (
              <div>
                <h3 className="text-lg font-bold text-purple-400 mb-3">LONG TERM</h3>
                <div className="space-y-2 ml-4">
                  {results.actionPlan.longTerm.map((item, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                      <div>
                        <div className="text-white">{item.title}</div>
                        <div className="text-sm text-gray-400">{item.reason} • ~{item.hours}hr</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Dynamic Meta Loop */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-cyan-500/30 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-3">🎯 Your Personalized Loop</h3>
            <div className="space-y-3">
              {generatePersonalizedLoop().map(step => (
                <div key={step.num} className="flex items-start gap-3">
                  <div className={\`w-8 h-8 rounded-full bg-\${step.color}-500 flex items-center justify-center text-white text-sm font-bold\`}>
                    {step.num}
                  </div>
                  <div>
                    <div className="text-white font-medium">{step.action}</div>
                    <div className="text-gray-400 text-sm">{step.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Meta Tips */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">2026 Meta Optimization</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-900/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Building className="w-5 h-5 text-blue-400" />
                  <div className="font-bold text-white">Passive Priority</div>
                </div>
                <div className="text-sm text-gray-300">
                  1. Nightclub (5 techs) → 2. Acid Lab (upgraded) → 3. Bunker
                </div>
              </div>
              <div className="p-4 bg-gray-900/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Car className="w-5 h-5 text-yellow-400" />
                  <div className="font-bold text-white">Travel Meta</div>
                </div>
                <div className="text-sm text-gray-300">
                  Sparrow (setups) → Oppressor Mk II (freeroam) → Imani Tech (sales)
                </div>
              </div>
              <div className="p-4 bg-gray-900/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Sword className="w-5 h-5 text-red-400" />
                  <div className="font-bold text-white">Stat Thresholds</div>
                </div>
                <div className="text-sm text-gray-300">
                  Strength 3+ → Flying 4+ → Shooting 4+
                </div>
              </div>
              <div className="p-4 bg-gray-900/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <div className="font-bold text-white">Income Loop</div>
                </div>
                <div className="text-sm text-gray-300">
                  Cayo → Payphone Hits → Passive collections → Repeat
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // FORM - Abbreviated for space, use your paste.txt form structure
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950 p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">GTA Online 2026 Meta Assessment</h1>
            <p className="text-gray-400">Accurate mechanics, realistic income calculations</p>
          </div>
          {/* INSERT YOUR COMPLETE FORM FROM PASTE.TXT HERE */}
          {/* Add new fields: cayoAvgTime, recentIncome, securityContractsDone */}
          <button
            onClick={calculateAssessment}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-4 rounded-xl transition-all">
            Calculate 2026 Meta Assessment
          </button>
        </div>
      </div>
    </div>
  );
}

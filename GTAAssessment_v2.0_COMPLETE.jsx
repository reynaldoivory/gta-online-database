import React, { useState } from 'react';
import { AlertCircle, Target, Zap, Award, TrendingUp, Building, Car, Sword, ChevronDown, ChevronUp, Info } from 'lucide-react';

export default function GTAMetaAssessment() {
  const [step, setStep] = useState('form');
  const [isCalculating, setIsCalculating] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    stats: true,
    active: true,
    passive: true,
    travel: true,
    playstyle: true
  });

  const [formData, setFormData] = useState({
    rank: '',
    timePlayed: '',
    liquidCash: '',
    totalIncome: '',
    recentIncome: '',
    strength: '',
    flying: '',
    shooting: '',
    stamina: '',
    stealth: '',
    lungCapacity: '',
    hasKosatka: false,
    hasSparrow: false,
    cayoCompletions: '',
    cayoAvgTime: '',
    hasAgency: false,
    dreContractDone: false,
    securityContractsDone: '',
    payphoneHitsDone: '',
    hasAcidLab: false,
    acidLabUpgraded: false,
    hasNightclub: false,
    nightclubTechs: '',
    nightclubLinked: [],
    hasBunker: false,
    bunkerUpgraded: false,
    hasMcCocaine: false,
    hasMcMeth: false,
    hasMcCash: false,
    hasCargoWarehouse: false,
    primaryTravel: 'car',
    hasOppressorMkII: false,
    hasArmoredKuruma: false,
    hasImaniTech: false,
    playMode: 'solo',
    checksWeeklyBonuses: false,
  });

  const [results, setResults] = useState(null);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

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

  const getLoopStepColor = (color) => {
    const colorMap = {
      green: 'bg-green-500',
      red: 'bg-red-500',
      blue: 'bg-blue-500',
      yellow: 'bg-yellow-500',
      purple: 'bg-purple-500'
    };
    return colorMap[color] || 'bg-gray-500';
  };

  const calculateAssessment = async () => {
    setIsCalculating(true);
    await new Promise(resolve => setTimeout(resolve, 300));

    const rank = parseInt(formData.rank) || 0;
    const timePlayed = parseInt(formData.timePlayed) || 1;
    const totalIncome = parseInt(formData.totalIncome) || 0;
    const recentIncome = parseInt(formData.recentIncome) || 0;
    const recentHours = Math.min(10, timePlayed);

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

    // STATS
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

    // PASSIVE INCOME - AWAITING DEV 2 FIXES
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

    // Agency Safe - DEV 2 FIXED TO 7/5/3/1
    const securityContracts = parseInt(formData.securityContractsDone) || 0;
    if (formData.hasAgency && formData.dreContractDone && securityContracts > 0) {
      let agencySafeScore = 0;
      let agencySafeIncome = 0;

      if (securityContracts >= 200) {
        agencySafeScore = 7;
        agencySafeIncome = 25000;
      } else if (securityContracts >= 100) {
        agencySafeScore = 5;
        agencySafeIncome = 20000;
      } else if (securityContracts >= 50) {
        agencySafeScore = 3;
        agencySafeIncome = 15000;
      } else {
        agencySafeScore = 1;
        agencySafeIncome = 10000;
      }

      breakdown.passive.score += agencySafeScore;
      passiveIncomePerHour += agencySafeIncome;

      if (securityContracts < 200) {
        breakdown.passive.issues.push('Agency safe not maxed');
      }
    }

    // Acid Lab - DEV 2 WILL FIX TO 5/3
    if (formData.hasAcidLab) {
      if (formData.acidLabUpgraded) {
        breakdown.passive.score += 5; // DEV 2 fixing from 7
        passiveIncomePerHour += 80000;
      } else {
        breakdown.passive.score += 3; // DEV 2 fixing from 4
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

    // Bunker - DEV 2 WILL FIX TO 3/1
    if (formData.hasBunker) {
      if (formData.bunkerUpgraded) {
        breakdown.passive.score += 3; // DEV 2 fixing from 5
        passiveIncomePerHour += 60000;
      } else {
        breakdown.passive.score += 1; // DEV 2 fixing from 2
        passiveIncomePerHour += 30000;
      }
    }

    // ACTIVE INCOME
    if (formData.hasKosatka) {
      const cayoRuns = parseInt(formData.cayoCompletions) || 0;
      const cayoTime = parseInt(formData.cayoAvgTime) || 120;

      let cayoScore = 3;
      let cayoIncome = 0;

      if (formData.hasSparrow) {
        cayoScore += 2;

        if (cayoTime <= 50 && cayoRuns >= 5) {
          cayoScore += 10;
          cayoIncome = 900000;
        } else if (cayoTime <= 65 && cayoRuns >= 3) {
          cayoScore += 6;
          cayoIncome = 750000;
        } else if (cayoTime <= 85 && cayoRuns >= 1) {
          cayoScore += 4;
          cayoIncome = 600000;
        } else if (cayoRuns >= 1) {
          cayoScore += 2;
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

      breakdown.active.score += cayoScore; // DEV 2 removed cap
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

    if (formData.hasAgency) {
      let agencyScore = 2;

      if (formData.dreContractDone) {
        agencyScore += 2;

        const payphoneHits = parseInt(formData.payphoneHitsDone) || 0;
        if (payphoneHits >= 10) {
          agencyScore += 4;
          activeIncomePerHour += 255000;
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

    breakdown.active.score += formData.checksWeeklyBonuses ? 2 : 0;

    // TRAVEL
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

    // ECONOMIC
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

    score = 
      breakdown.stats.score + 
      breakdown.passive.score + 
      breakdown.active.score + 
      breakdown.travel.score + 
      breakdown.economic.score;

    // TIER
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

    // ACTION PLAN
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

    setIsCalculating(false);
    setStep('results');
  };

  const generatePersonalizedLoop = () => {
    if (!results) return [];

    const steps = [];

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

  // Tooltip Component
  const Tooltip = ({ text }) => (
    <div className="group relative inline-block ml-1">
      <Info className="w-4 h-4 text-gray-500 cursor-help" />
      <div className="hidden group-hover:block absolute z-10 w-64 p-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg bottom-full left-1/2 transform -translate-x-1/2 mb-2">
        {text}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  );

  if (step === 'results' && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950 p-4 md:p-6">
        <div className="max-w-6xl mx-auto space-y-6">
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

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6">
              <div className="flex items-center gap-4 mb-6">
                <Award className="w-12 h-12 text-yellow-400" />
                <div>
                  <div className="text-5xl font-bold text-white">{results.score}<span className="text-2xl text-gray-400">/100</span></div>
                  <div className={`text-xl font-bold mt-2 ${results.tierColor}`}>{results.tier}</div>
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
                        width: `${(data.score / data.max) * 100}%`,
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
                    className={`p-4 rounded-xl ${
                      bottleneck.critical 
                        ? 'bg-red-900/20 border border-red-700/30' 
                        : 'bg-orange-900/20 border border-orange-700/30'
                    }`}
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

          <div className="bg-gray-800/50 backdrop-blur-sm border border-cyan-500/30 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-3">🎯 Your Personalized Loop</h3>
            <div className="space-y-3">
              {generatePersonalizedLoop().map(step => (
                <div key={step.num} className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full ${getLoopStepColor(step.color)} flex items-center justify-center text-white text-sm font-bold`}>
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

  // FORM WITH COMPLETE COLLAPSIBLE SECTIONS
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950 p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 md:p-8">
          <div className="mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">GTA Online 2026 Meta Assessment</h1>
            <p className="text-gray-400 text-sm md:text-base">Accurate mechanics, realistic income calculations • v2.0</p>
          </div>

          <div className="space-y-6">
            {/* Account Basics */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-white border-b border-gray-700 pb-2">Account Basics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Rank</label>
                  <input
                    type="number"
                    value={formData.rank}
                    onChange={(e) => handleInputChange('rank', e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-purple-500 focus:outline-none"
                    placeholder="33"
                    min="1"
                    max="8000"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Hours Played</label>
                  <input
                    type="number"
                    value={formData.timePlayed}
                    onChange={(e) => handleInputChange('timePlayed', e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-purple-500 focus:outline-none"
                    placeholder="57"
                    min="1"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Cash in Bank ($)</label>
                  <input
                    type="number"
                    value={formData.liquidCash}
                    onChange={(e) => handleInputChange('liquidCash', e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-purple-500 focus:outline-none"
                    placeholder="1900000"
                    min="0"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Total Income ($)</label>
                  <input
                    type="number"
                    value={formData.totalIncome}
                    onChange={(e) => handleInputChange('totalIncome', e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-purple-500 focus:outline-none"
                    placeholder="9500000"
                    min="0"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm text-gray-300 mb-1 flex items-center">
                    Recent Income ($)
                    <Tooltip text="Money earned in your last ~10 hours of active play. This shows your current grinding efficiency." />
                  </label>
                  <input
                    type="number"
                    value={formData.recentIncome}
                    onChange={(e) => handleInputChange('recentIncome', e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-purple-500 focus:outline-none"
                    placeholder="3000000"
                    min="0"
                  />
                </div>
              </div>
            </div>

            {/* Character Stats */}
            <div className="space-y-4">
              <button
                onClick={() => toggleSection('stats')}
                className="w-full flex items-center justify-between text-xl font-bold text-white border-b border-gray-700 pb-2 hover:text-purple-400 transition"
              >
                <span>Character Stats</span>
                {expandedSections.stats ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
              {expandedSections.stats && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[
                    { key: 'strength', label: 'Strength', critical: true, tooltip: 'Critical for damage resistance and melee. Aim for 3+ minimum.' },
                    { key: 'flying', label: 'Flying', critical: true, tooltip: 'Critical for helicopter control. 4+ for smooth Sparrow flying.' },
                    { key: 'shooting', label: 'Shooting', critical: false, tooltip: 'Improves accuracy and reload speed. 3+ recommended.' },
                    { key: 'stamina', label: 'Stamina', critical: false, tooltip: 'Affects sprint duration. Less critical but helpful.' },
                    { key: 'stealth', label: 'Stealth', critical: false, tooltip: 'Useful for Cayo Perico drainage tunnel approach.' },
                    { key: 'lungCapacity', label: 'Lung Capacity', critical: false, tooltip: 'Needed for Cayo drainage tunnel. 3+ recommended.' }
                  ].map(stat => (
                    <div key={stat.key}>
                      <label className="block text-sm text-gray-300 mb-1 flex items-center">
                        {stat.label} {stat.critical && <span className="text-red-400 ml-1">*</span>}
                        <Tooltip text={stat.tooltip} />
                      </label>
                      <select
                        value={formData[stat.key]}
                        onChange={(e) => handleInputChange(stat.key, e.target.value)}
                        className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-purple-500 focus:outline-none text-sm"
                      >
                        <option value="">Select</option>
                        {[5,4,3,2,1,0].map(val => (
                          <option key={val} value={val}>{val}/5</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Active Income */}
            <div className="space-y-4">
              <button
                onClick={() => toggleSection('active')}
                className="w-full flex items-center justify-between text-xl font-bold text-white border-b border-gray-700 pb-2 hover:text-purple-400 transition"
              >
                <span>Active Income Assets</span>
                {expandedSections.active ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
              {expandedSections.active && (
                <div className="space-y-6">
                  {/* Kosatka */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        type="checkbox"
                        checked={formData.hasKosatka}
                        onChange={(e) => handleInputChange('hasKosatka', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Kosatka Submarine
                        <Tooltip text="The #1 solo money maker. Enables Cayo Perico heist ($900k-1.5M per run)." />
                      </label>
                    </div>
                    {formData.hasKosatka && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 ml-7">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <input
                              type="checkbox"
                              checked={formData.hasSparrow}
                              onChange={(e) => handleInputChange('hasSparrow', e.target.checked)}
                              className="w-4 h-4"
                            />
                            <label className="text-sm text-gray-300 flex items-center">
                              Sparrow Helicopter
                              <Tooltip text="Spawns instantly next to you. Makes setups 2x faster than CEO Buzzard." />
                            </label>
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm text-gray-300 mb-1">Cayo Completions</label>
                          <input
                            type="number"
                            value={formData.cayoCompletions}
                            onChange={(e) => handleInputChange('cayoCompletions', e.target.value)}
                            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                            placeholder="0"
                            min="0"
                          />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-300 mb-1 flex items-center">
                            Average Time (minutes)
                            <Tooltip text="Full run time (setup + heist). Elite: <50min, Pro: 50-65min, Learning: 65-85min." />
                          </label>
                          <input
                            type="number"
                            value={formData.cayoAvgTime}
                            onChange={(e) => handleInputChange('cayoAvgTime', e.target.value)}
                            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                            placeholder="75"
                            min="30"
                            max="180"
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Agency */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        type="checkbox"
                        checked={formData.hasAgency}
                        onChange={(e) => handleInputChange('hasAgency', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Agency
                        <Tooltip text="Enables Payphone Hits ($85k/20min) and passive safe income ($25k/hr max)." />
                      </label>
                    </div>
                    {formData.hasAgency && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 ml-7">
                        <div>
                          <div className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.dreContractDone}
                              onChange={(e) => handleInputChange('dreContractDone', e.target.checked)}
                              className="w-4 h-4"
                            />
                            <label className="text-sm text-gray-300 flex items-center">
                              Dr. Dre Contract Done
                              <Tooltip text="$1M one-time payout. Unlocks Payphone Hits." />
                            </label>
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm text-gray-300 mb-1">Payphone Hits Done</label>
                          <input
                            type="number"
                            value={formData.payphoneHitsDone}
                            onChange={(e) => handleInputChange('payphoneHitsDone', e.target.value)}
                            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                            placeholder="0"
                            min="0"
                          />
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm text-gray-300 mb-1 flex items-center">
                            Security Contracts Done
                            <Tooltip text="Increases Agency safe capacity. 200+ = $25k/hr passive income." />
                          </label>
                          <input
                            type="number"
                            value={formData.securityContractsDone}
                            onChange={(e) => handleInputChange('securityContractsDone', e.target.value)}
                            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                            placeholder="0"
                            min="0"
                            max="500"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Passive Income */}
            <div className="space-y-4">
              <button
                onClick={() => toggleSection('passive')}
                className="w-full flex items-center justify-between text-xl font-bold text-white border-b border-gray-700 pb-2 hover:text-purple-400 transition"
              >
                <span>Passive Income Assets</span>
                {expandedSections.passive ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
              {expandedSections.passive && (
                <div className="space-y-6">
                  {/* Nightclub */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        type="checkbox"
                        checked={formData.hasNightclub}
                        onChange={(e) => handleInputChange('hasNightclub', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Nightclub
                        <Tooltip text="The passive income king. $50k/hr when fully set up with 5 technicians and 5 linked businesses." />
                      </label>
                    </div>
                    {formData.hasNightclub && (
                      <div className="mt-3 ml-7 space-y-4">
                        <div>
                          <label className="block text-sm text-gray-300 mb-2">Technicians Assigned</label>
                          <select
                            value={formData.nightclubTechs}
                            onChange={(e) => handleInputChange('nightclubTechs', e.target.value)}
                            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                          >
                            <option value="">Select</option>
                            {[5,4,3,2,1,0].map(val => (
                              <option key={val} value={val}>{val}/5</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm text-gray-300 mb-2">Linked Businesses (check all owned)</label>
                          <div className="space-y-2">
                            {[
                              { key: 'cargo', label: 'Cargo Warehouse', tooltip: 'Provides Cargo & Shipments' },
                              { key: 'bunker', label: 'Bunker', tooltip: 'Provides Sporting Goods' },
                              { key: 'coke', label: 'MC Cocaine', tooltip: 'Provides South American Imports' },
                              { key: 'meth', label: 'MC Meth', tooltip: 'Provides Pharmaceutical Research' },
                              { key: 'cash', label: 'MC Cash', tooltip: 'Provides Cash Creation' }
                            ].map(biz => (
                              <div key={biz.key} className="flex items-center gap-2">
                                <input
                                  type="checkbox"
                                  checked={formData.nightclubLinked.includes(biz.key)}
                                  onChange={() => handleLinkedToggle(biz.key)}
                                  className="w-4 h-4"
                                />
                                <label className="text-sm text-gray-300 flex items-center">
                                  {biz.label}
                                  <Tooltip text={biz.tooltip} />
                                </label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Acid Lab */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        type="checkbox"
                        checked={formData.hasAcidLab}
                        onChange={(e) => handleInputChange('hasAcidLab', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Acid Lab
                        <Tooltip text="Easiest passive setup. $80k/hr when upgraded." />
                      </label>
                    </div>
                    {formData.hasAcidLab && (
                      <div className="mt-3 ml-7">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData.acidLabUpgraded}
                            onChange={(e) => handleInputChange('acidLabUpgraded', e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label className="text-sm text-gray-300">Equipment Upgrade</label>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Bunker */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        type="checkbox"
                        checked={formData.hasBunker}
                        onChange={(e) => handleInputChange('hasBunker', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Bunker
                        <Tooltip text="$60k/hr passive when upgraded. Also needed for Nightclub." />
                      </label>
                    </div>
                    {formData.hasBunker && (
                      <div className="mt-3 ml-7">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData.bunkerUpgraded}
                            onChange={(e) => handleInputChange('bunkerUpgraded', e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label className="text-sm text-gray-300">Equipment + Staff Upgrades</label>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* MC Businesses */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <label className="text-white font-medium mb-3 block flex items-center">
                      MC Businesses
                      <Tooltip text="Needed for Nightclub feeder businesses. Don't need to be upgraded." />
                    </label>
                    <div className="space-y-2 ml-3">
                      {[
                        { key: 'hasMcCocaine', label: 'Cocaine Lockup' },
                        { key: 'hasMcMeth', label: 'Meth Lab' },
                        { key: 'hasMcCash', label: 'Counterfeit Cash' }
                      ].map(biz => (
                        <div key={biz.key} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData[biz.key]}
                            onChange={(e) => handleInputChange(biz.key, e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label className="text-sm text-gray-300">{biz.label}</label>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Cargo Warehouse */}
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.hasCargoWarehouse}
                        onChange={(e) => handleInputChange('hasCargoWarehouse', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Cargo Warehouse
                        <Tooltip text="Needed for Nightclub 5th technician slot (Cargo & Shipments)." />
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Travel & Vehicles */}
            <div className="space-y-4">
              <button
                onClick={() => toggleSection('travel')}
                className="w-full flex items-center justify-between text-xl font-bold text-white border-b border-gray-700 pb-2 hover:text-purple-400 transition"
              >
                <span>Travel & Vehicles</span>
                {expandedSections.travel ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
              {expandedSections.travel && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-300 mb-2 flex items-center">
                      Primary Travel Method
                      <Tooltip text="How you get around Los Santos. Air travel saves 5-10 minutes per mission." />
                    </label>
                    <select
                      value={formData.primaryTravel}
                      onChange={(e) => handleInputChange('primaryTravel', e.target.value)}
                      className="w-full bg-gray-700 text-white rounded-lg px-3 py-2"
                    >
                      <option value="car">Car</option>
                      <option value="mixed">Mixed (car + occasional air)</option>
                      <option value="buzzard">CEO Buzzard</option>
                      <option value="sparrow">Sparrow</option>
                      <option value="oppressor">Oppressor Mk II</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-white font-medium mb-3 block">Combat Vehicles</label>
                    <div className="space-y-2 ml-3">
                      {[
                        { key: 'hasOppressorMkII', label: 'Oppressor Mk II', tooltip: 'Best all-around vehicle. Fast travel + missiles.' },
                        { key: 'hasArmoredKuruma', label: 'Armored Kuruma', tooltip: 'Budget option. Bulletproof, great for contact missions.' },
                        { key: 'hasImaniTech', label: 'Imani Tech Vehicle', tooltip: 'Missile lock-on jammer. Excellent for sales in public lobbies.' }
                      ].map(vehicle => (
                        <div key={vehicle.key} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData[vehicle.key]}
                            onChange={(e) => handleInputChange(vehicle.key, e.target.checked)}
                            className="w-4 h-4"
                          />
                          <label className="text-sm text-gray-300 flex items-center">
                            {vehicle.label}
                            <Tooltip text={vehicle.tooltip} />
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Playstyle */}
            <div className="space-y-4">
              <button
                onClick={() => toggleSection('playstyle')}
                className="w-full flex items-center justify-between text-xl font-bold text-white border-b border-gray-700 pb-2 hover:text-purple-400 transition"
              >
                <span>Playstyle</span>
                {expandedSections.playstyle ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
              {expandedSections.playstyle && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-300 mb-2 flex items-center">
                      Primary Play Mode
                      <Tooltip text="Solo Cayo cooldown: 144 min (2h24m). Crew Cayo: 48 min." />
                    </label>
                    <select
                      value={formData.playMode}
                      onChange={(e) => handleInputChange('playMode', e.target.value)}
                      className="w-full bg-gray-700 text-white rounded-lg px-3 py-2"
                    >
                      <option value="solo">Solo Player</option>
                      <option value="crew">Crew/Friends</option>
                    </select>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.checksWeeklyBonuses}
                        onChange={(e) => handleInputChange('checksWeeklyBonuses', e.target.checked)}
                        className="w-5 h-5"
                      />
                      <label className="text-white font-medium flex items-center">
                        Checks Weekly Bonuses
                        <Tooltip text="Rockstar updates bonuses every Thursday. 2x$ events can double your income." />
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={calculateAssessment}
              disabled={isCalculating}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-8"
            >
              {isCalculating ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Calculating...
                </span>
              ) : (
                'Calculate 2026 Meta Assessment'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2014 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_CONSENSUS_PARAMS_H
#define BITCOIN_CONSENSUS_PARAMS_H

#include "amount.h"
#include "uint256.h"

#include <memory>

namespace Consensus {

/**
 * Interface for classes that define consensus behaviour in more
 * complex ways than just by a set of constants.
 */
class ConsensusRules
{
public:

    /* Return the expiration depth for names at the given height.  */
    virtual unsigned NameExpirationDepth(unsigned nHeight) const = 0;

    /* Return minimum locked amount in a name.  */
    virtual CAmount MinNameCoinAmount(unsigned nHeight) const = 0;

};

class MainNetConsensus : public ConsensusRules
{
public:

    unsigned NameExpirationDepth(unsigned nHeight) const
    {
        /* Important:  It is assumed (in ExpireNames) that
           "n - expirationDepth(n)" is increasing!  (This is
           the update height up to which names expire at height n.)  */

        if (nHeight < 24000)
            return 12000;
        if (nHeight < 48000)
            return nHeight - 12000;

        return 36000;
    }

    CAmount MinNameCoinAmount(unsigned nHeight) const
    {
        if (nHeight < 212500)
            return 0;

        return COIN / 100;
    }

};

class TestNetConsensus : public MainNetConsensus
{
public:

    CAmount MinNameCoinAmount(unsigned) const
    {
        return COIN / 100;
    }

};

class RegTestConsensus : public TestNetConsensus
{
public:

    unsigned NameExpirationDepth (unsigned nHeight) const
    {
        return 30;
    }

};

/**
 * Parameters that influence chain consensus.
 */
struct Params {
    uint256 hashGenesisBlock;
    int nSubsidyHalvingInterval;
    /** Used to check majorities for block version upgrade */
    int nMajorityEnforceBlockUpgrade;
    int nMajorityRejectBlockOutdated;
    int nMajorityWindow;
    /** Proof of work parameters */
    uint256 powLimit;
    bool fPowAllowMinDifficultyBlocks;
    int64_t nMinDifficultySince;
    int64_t nPowTargetSpacing;
    int64_t nPowTargetTimespan;
    int64_t DifficultyAdjustmentInterval() const { return nPowTargetTimespan / nPowTargetSpacing; }
    /** Auxpow parameters */
    int32_t nAuxpowChainId;
    int nAuxpowStartHeight;
    bool fStrictChainId;
    int nLegacyBlocksBefore; // -1 for "always allow"

    /** Consensus rule interface.  */
    std::auto_ptr<ConsensusRules> rules;

    /**
     * Check whether or not minimum difficulty blocks are allowed
     * with the given time stamp.
     * @param nBlockTime Time of the block with minimum difficulty.
     * @return True if it is allowed to have minimum difficulty.
     */
    bool AllowMinDifficultyBlocks(int64_t nBlockTime) const
    {
        if (!fPowAllowMinDifficultyBlocks)
            return false;
        return nBlockTime > nMinDifficultySince;
    }

    /**
     * Check whether or not to allow legacy blocks at the given height.
     * @param nHeight Height of the block to check.
     * @return True if it is allowed to have a legacy version.
     */
    bool AllowLegacyBlocks(unsigned nHeight) const
    {
        if (nLegacyBlocksBefore < 0)
            return true;
        return static_cast<int> (nHeight) < nLegacyBlocksBefore;
    }
};
} // namespace Consensus

#endif // BITCOIN_CONSENSUS_PARAMS_H
